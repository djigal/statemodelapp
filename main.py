from dataclasses import dataclass, field
from typing import Protocol
from enum import Enum, auto

from sm import StateMachine

class PayStateEnum(Enum):
    NEW = auto()
    AUTHORIZED = auto()
    REFUNDED = auto()
    CAPTURED = auto()
    FAILED = auto()

class PayEventEnum(Enum):
    AUTHORIZE = auto()
    REFUND = auto()
    CAPTURE = auto()
    FAIL = auto()

@dataclass
class PaymentCtx:
    payment_id: str
    audit: list[str] = field(default_factory=list[str])


pay_sm: StateMachine[PayStateEnum, PayEventEnum, PaymentCtx] = StateMachine()

@pay_sm.transition(PayStateEnum.NEW, PayEventEnum.AUTHORIZE, PayStateEnum.AUTHORIZED)
def authorize(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: authorized.")

@pay_sm.transition((PayStateEnum.NEW, PayStateEnum.AUTHORIZED), PayEventEnum.FAIL, PayStateEnum.FAILED)
def fail(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: failed.")

@pay_sm.transition((PayStateEnum.AUTHORIZED, PayStateEnum.CAPTURED), PayEventEnum.REFUND, PayStateEnum.REFUNDED)
def refund(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: refunded.")

@pay_sm.transition(PayStateEnum.AUTHORIZED, PayEventEnum.CAPTURE, PayStateEnum.CAPTURED)
def capture( ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: captured.")

@dataclass
class Payment:
    ctx: PaymentCtx
    state: PayStateEnum = field(default=PayStateEnum.NEW)

    def handle(self, event: PayEventEnum) -> None:
        self.state = pay_sm.handle(self.state, event, self.ctx)

def main() -> None:
    payment = Payment(ctx=PaymentCtx(payment_id="1234") )

    payment.handle(PayEventEnum.AUTHORIZE)
    # payment.handle(PayEventEnum.FAIL)
    payment.handle(PayEventEnum.CAPTURE)
    payment.handle(PayEventEnum.REFUND)

    print("final state:", type(payment.state))
    print("audit: ", payment.ctx.audit)


if __name__ == "__main__":
    main()