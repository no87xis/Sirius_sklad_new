from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import PaymentMethodModel, PaymentInstrument, CashFlow, Order


class PaymentService:
    """Сервис для работы с платежами и движением денег"""
    
    @staticmethod
    def get_active_payment_methods(db: Session) -> list[PaymentMethodModel]:
        """Получает активные методы оплаты"""
        return db.query(PaymentMethodModel).filter(PaymentMethodModel.is_active == True).all()
    
    @staticmethod
    def get_payment_method_by_id(db: Session, method_id: int) -> PaymentMethodModel:
        """Получает метод оплаты по ID"""
        return db.query(PaymentMethodModel).filter(PaymentMethodModel.id == method_id).first()
    
    @staticmethod
    def get_payment_method_by_name(db: Session, name: str) -> PaymentMethodModel:
        """Получает метод оплаты по названию"""
        return db.query(PaymentMethodModel).filter(PaymentMethodModel.name == name).first()
    
    @staticmethod
    def create_payment_method(db: Session, name: str, type: str = None) -> PaymentMethodModel:
        """Создает новый метод оплаты"""
        payment_method = PaymentMethodModel(
            name=name,
            type=type,
            is_active=True
        )
        db.add(payment_method)
        db.commit()
        db.refresh(payment_method)
        return payment_method
    
    @staticmethod
    def get_instruments_by_method(db: Session, method_id: int) -> list[PaymentInstrument]:
        """Получает инструменты для конкретного метода оплаты"""
        return db.query(PaymentInstrument).filter(
            PaymentInstrument.method_id == method_id,
            PaymentInstrument.is_active == True
        ).all()
    
    @staticmethod
    def get_instrument_by_id(db: Session, instrument_id: int) -> PaymentInstrument:
        """Получает инструмент оплаты по ID"""
        return db.query(PaymentInstrument).filter(PaymentInstrument.id == instrument_id).first()
    
    @staticmethod
    def create_payment_instrument(db: Session, name: str, method_id: int) -> PaymentInstrument:
        """Создает новый инструмент оплаты"""
        instrument = PaymentInstrument(
            name=name,
            method_id=method_id,
            is_active=True
        )
        db.add(instrument)
        db.commit()
        db.refresh(instrument)
        return instrument
    
    @staticmethod
    def record_payment(db: Session, order_id: int, method_id: int, 
                      instrument_id: int = None, amount: Decimal = None) -> CashFlow:
        """Записывает оплату заказа"""
        # Создаем запись о приходе денег
        cash_flow = CashFlow(
            datetime=datetime.utcnow(),
            direction="INFLOW",
            source_method_id=method_id,
            source_instrument_id=instrument_id,
            amount=amount or Decimal("0"),
            reason=f"Оплата заказа #{order_id}",
            order_id=order_id
        )
        db.add(cash_flow)
        
        # Обновляем заказ
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.payment_method_id = method_id
            order.payment_instrument_id = instrument_id
            order.paid_amount = amount
            order.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cash_flow)
        return cash_flow
    
    @staticmethod
    def record_cash_outflow(db: Session, method_id: int, amount: Decimal, 
                           reason: str, instrument_id: int = None) -> CashFlow:
        """Записывает выемку/снятие средств"""
        cash_flow = CashFlow(
            datetime=datetime.utcnow(),
            direction="OUTFLOW",
            source_method_id=method_id,
            source_instrument_id=instrument_id,
            amount=amount,
            reason=reason
        )
        db.add(cash_flow)
        db.commit()
        db.refresh(cash_flow)
        return cash_flow
    
    @staticmethod
    def get_cash_balance(db: Session, method_id: int = None, 
                        instrument_id: int = None) -> dict:
        """Получает баланс по методам/инструментам оплаты"""
        query = db.query(CashFlow)
        
        if method_id:
            query = query.filter(CashFlow.source_method_id == method_id)
        if instrument_id:
            query = query.filter(CashFlow.source_instrument_id == instrument_id)
        
        cash_flows = query.all()
        
        total_inflow = sum(cf.amount for cf in cash_flows if cf.direction == "INFLOW")
        total_outflow = sum(cf.amount for cf in cash_flows if cf.direction == "OUTFLOW")
        
        return {
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "balance": total_inflow - total_outflow,
            "transactions_count": len(cash_flows)
        }
    
    @staticmethod
    def get_payment_analytics(db: Session, start_date: datetime = None, 
                             end_date: datetime = None) -> dict:
        """Получает аналитику по платежам за период"""
        query = db.query(CashFlow)
        
        if start_date:
            query = query.filter(CashFlow.datetime >= start_date)
        if end_date:
            query = query.filter(CashFlow.datetime <= end_date)
        
        cash_flows = query.all()
        
        # Группируем по методам оплаты
        methods_analytics = {}
        for cf in cash_flows:
            method_name = cf.source_method.name
            if method_name not in methods_analytics:
                methods_analytics[method_name] = {
                    "inflow": Decimal("0"),
                    "outflow": Decimal("0"),
                    "balance": Decimal("0"),
                    "transactions": []
                }
            
            if cf.direction == "INFLOW":
                methods_analytics[method_name]["inflow"] += cf.amount
            else:
                methods_analytics[method_name]["outflow"] += cf.amount
            
            methods_analytics[method_name]["transactions"].append({
                "id": cf.id,
                "datetime": cf.datetime,
                "direction": cf.direction,
                "amount": cf.amount,
                "reason": cf.reason,
                "order_id": cf.order_id
            })
        
        # Вычисляем баланс для каждого метода
        for method_data in methods_analytics.values():
            method_data["balance"] = method_data["inflow"] - method_data["outflow"]
        
        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "total_inflow": sum(cf.amount for cf in cash_flows if cf.direction == "INFLOW"),
            "total_outflow": sum(cf.amount for cf in cash_flows if cf.direction == "OUTFLOW"),
            "methods_analytics": methods_analytics
        }
