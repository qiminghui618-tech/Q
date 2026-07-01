"""Price alert and notification system"""
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PriceAlert:
    """Price alert definition"""
    
    def __init__(
        self,
        symbol: str,
        alert_type: str,  # above, below
        target_price: float,
        alert_id: Optional[str] = None
    ):
        self.symbol = symbol
        self.alert_type = alert_type
        self.target_price = target_price
        self.alert_id = alert_id or f"{symbol}_{alert_type}_{target_price}_{datetime.now().timestamp()}"
        self.created_at = datetime.now()
        self.triggered = False
        self.triggered_at = None
    
    def should_trigger(self, current_price: float) -> bool:
        """Check if alert should be triggered"""
        if self.triggered:
            return False
        
        if self.alert_type == "above" and current_price >= self.target_price:
            return True
        elif self.alert_type == "below" and current_price <= self.target_price:
            return True
        
        return False
    
    def mark_triggered(self):
        """Mark alert as triggered"""
        self.triggered = True
        self.triggered_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'target_price': self.target_price,
            'created_at': self.created_at.isoformat(),
            'triggered': self.triggered,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None
        }


class AlertManager:
    """Manage price alerts"""
    
    def __init__(self):
        self.alerts: Dict[str, List[PriceAlert]] = {}
        self.notification_callbacks: List[Callable] = []
        self.alert_history: List[Dict] = []
    
    def create_alert(
        self,
        symbol: str,
        alert_type: str,
        target_price: float
    ) -> PriceAlert:
        """
        Create a new price alert
        
        Args:
            symbol: Stock symbol
            alert_type: "above" or "below"
            target_price: Target price for alert
        
        Returns:
            Created PriceAlert object
        """
        if symbol not in self.alerts:
            self.alerts[symbol] = []
        
        alert = PriceAlert(symbol, alert_type, target_price)
        self.alerts[symbol].append(alert)
        
        logger.info(f"Created alert: {symbol} {alert_type} ${target_price}")
        return alert
    
    def check_alerts(self, symbol: str, current_price: float):
        """
        Check if any alerts should be triggered
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
        """
        if symbol not in self.alerts:
            return
        
        for alert in self.alerts[symbol]:
            if alert.should_trigger(current_price):
                alert.mark_triggered()
                self._notify_alert(alert, current_price)
                self.alert_history.append({
                    'alert': alert.to_dict(),
                    'trigger_price': current_price,
                    'triggered_at': datetime.now().isoformat()
                })
    
    def get_alerts(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all active alerts"""
        if symbol:
            if symbol in self.alerts:
                return [alert.to_dict() for alert in self.alerts[symbol] if not alert.triggered]
            return []
        
        result = []
        for alerts_list in self.alerts.values():
            result.extend([a.to_dict() for a in alerts_list if not a.triggered])
        return result
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        for symbol, alerts_list in self.alerts.items():
            for i, alert in enumerate(alerts_list):
                if alert.alert_id == alert_id:
                    alerts_list.pop(i)
                    logger.info(f"Deleted alert: {alert_id}")
                    return True
        return False
    
    def register_notification_callback(self, callback: Callable):
        """Register a callback for alerts"""
        self.notification_callbacks.append(callback)
    
    def _notify_alert(self, alert: PriceAlert, current_price: float):
        """Notify about triggered alert"""
        message = f"Alert triggered: {alert.symbol} {alert.alert_type} ${alert.target_price} - Current price: ${current_price:.2f}"
        logger.warning(message)
        
        # Call all registered callbacks
        for callback in self.notification_callbacks:
            try:
                callback({
                    'alert': alert.to_dict(),
                    'current_price': current_price,
                    'message': message
                })
            except Exception as e:
                logger.error(f"Error in notification callback: {str(e)}")


# Singleton instance
_alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get singleton alert manager"""
    return _alert_manager
