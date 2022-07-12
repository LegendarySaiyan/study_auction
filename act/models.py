import uuid

import django_fsm
import typing as tp
from django.db import models


class Customer(models.Model):
    """Профиль клиента"""

    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профиль клиента'

    uid = models.UUIDField(
        'UID',
        unique=True,
        default=uuid.uuid4,
    )
    statement_signed_at = models.DateTimeField(
        'Принял оферту',
        null=True,
        blank=True,
        help_text='Дата/Время подписания оферты',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True, help_text='Дата/Время создания записи')

    last_name = models.CharField(
        'Фамилия',
        max_length=64,
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=64,
        blank=True,
        null=True,
    )
    patronymic = models.CharField(
        'Отчество',
        max_length=64,
        blank=True,
        null=True,
    )
    mail = models.EmailField(max_length=254)

    @property
    def full_name(self) -> tp.Optional[str]:
        names = [name for name in (self.last_name, self.first_name, self.patronymic) if name is not None]
        return ' '.join(names).strip() or None

    def __str__(self):
        return self.full_name


class VirtualAccount(models.Model):
    """Виртуальный счет"""

    class Meta:
        verbose_name = 'Виртуальный счет'
        verbose_name_plural = 'Виртуальный счет'

    customer_profile = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='virtual_account',
    )
    balance = models.DecimalField('Баланс', default=0, decimal_places=2, max_digits=14)
    virtual_account_id = models.UUIDField('ID виртуального счета', unique=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True, help_text='Дата/Время создания записи')


class CustomerLotState(models.TextChoices):
    """Состояние лота"""

    WAITING_FOR_TRADES = 'waiting_for_trade', 'Ожидает начало торга'
    TRADING_IN_PROCESS = 'trading_in_process', 'В процессе торга'
    TRADING_IS_FINISHED = 'trading_is_finished', 'Торг завершен(Победитель не подтвержден)'
    WINNER_OF_TRADE_APPROVED = (
        'winner_of_trade_approved',
        'Торг завершен(Победитель подтвержден)',
    )
    PAYMENT_IN_PROCESS = 'payment_in_process', 'Оплата в процессе'
    PAYMENT_SUCCESS = 'payment_success', 'Оплата успешно завершена'
    PAYMENT_FAILED = 'payment_failed', 'Оплата завершена с ошибкой'


class CustomerLot(models.Model):
    class Meta:
        verbose_name = 'Лот клиента'
        verbose_name_plural = 'Лот клиента'

    PAYMENT_STATES = (
        CustomerLotState.PAYMENT_IN_PROCESS,
        CustomerLotState.PAYMENT_SUCCESS,
        CustomerLotState.PAYMENT_FAILED,
    )

    CONTRACTOR_DECLINE_ALLOWED_STATES = (
        # Клиенты могут отказаться от выкупа лота
        # Даем им возможность отказаться от лота с уплатой штрафа
        CustomerLotState.TRADING_IS_FINISHED,
    )

    PAYMENT_ALLOWED_STATES = (
        CustomerLotState.WINNER_OF_TRADE_APPROVED,
        CustomerLotState.PAYMENT_FAILED,
    )

    uid = models.UUIDField(
        'UID',
        unique=True,
        default=uuid.uuid4,
    )

    state = django_fsm.FSMField(
        'Состояние',
        choices=CustomerLotState.choices,
        default=CustomerLotState.WAITING_FOR_TRADES,
    )

    trade_winner = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text='Победитель торга',
        related_name='purchased_lot'
    )
    owner_customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        help_text='Владелец лота',
    )
    short_description = models.CharField(
        'Краткое описание',
        max_length=256,
        help_text='Краткое описание лота',
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True,
        help_text='Полное описание лота',
    )
    start_price = models.DecimalField(
        'Начальная стоимость',
        help_text='В рублях',
        max_digits=14,
        decimal_places=2,
    )
    final_price = models.DecimalField(
        'Финальная стоимость',
        null=True,
        blank=True,
        help_text='В рублях',
        max_digits=14,
        decimal_places=2,
    )
    commission = models.DecimalField(
        'Коммиссия',
        null=True,
        blank=True,
        help_text='Наша комиссия за торг',
        max_digits=14,
        decimal_places=2,
    )
    lot_image = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=300)
    trade_started_at = models.DateTimeField('Дата/Время начала торга', null=True, blank=True)
    payment_started_at = models.DateTimeField('Дата/Время начала оплаты', null=True, blank=True)
    paid_at = models.DateTimeField('Оплачено', help_text='Дата/Время оплаты', null=True, blank=True)
    created_at = models.DateTimeField('Добавлено', help_text='Дата/Время создания', auto_now_add=True)

    all_participants_info = models.JSONField('Все участники торгов', default=dict)


class CustomerLotPaymentState(models.TextChoices):
    """Состояние лота"""

    STARTED = 'started', 'Запущена'  #: Процесс оплаты запущен
    INSUFFICIENT_FUNDS_ON_VIRTUAL_ACCOUNT = (
        'insufficient_funds_on_virtual_account',
        'Недостаточно средств на счёте',
    )
    REJECTED = 'rejected', 'Оплата отклонена'
    PAID = 'paid', 'Оплата успешно завершена'


class CustomerLotPayment(models.Model):

    class Meta:
        verbose_name = 'Оплата лота'
        verbose_name_plural = 'Оплата лотов'

    State = CustomerLotPaymentState

    PAYMENT_FINISHED_STATES = (
        CustomerLotPaymentState.REJECTED,
        CustomerLotPaymentState.PAID,
    )

    PAYMENT_REJECT_ALLOWED_STATES = (
        CustomerLotPaymentState.INSUFFICIENT_FUNDS_ON_VIRTUAL_ACCOUNT,
    )
    REJECTED_DETAIL_MESSAGES = {
        CustomerLotPaymentState.INSUFFICIENT_FUNDS_ON_VIRTUAL_ACCOUNT: 'Недостаточно средств на счёте',
    }

    state = django_fsm.FSMField(
        'Состояние',
        choices=CustomerLotPaymentState.choices,
        default=CustomerLotPaymentState.STARTED,
    )
    CustomerLot = models.ForeignKey(
        CustomerLot,
        on_delete=models.CASCADE,
        related_name='payments',
        related_query_name='payment',
        help_text='Оплачиваемый лот',
    )
    uid = models.UUIDField(
        'UID',
        unique=True,
        default=uuid.uuid4,
    )
    paid_at = models.DateTimeField('Оплачено', help_text='Дата/Время оплаты', null=True, blank=True)
    rejected_at = models.DateTimeField('Отказано', help_text='Дата/Время отказа', null=True, blank=True)

    created_at = models.DateTimeField(
        'Процесс оплаты запущен',
        help_text='Дата/Время запуска процесса оплаты',
        auto_now_add=True,
    )
    finished = models.BooleanField(
        'Завершен',
        default=False,
        help_text=(
            'Если процесс завершен, то работа с ним не требуется.\n'
            'Вне зависимости от того, на какой стадии он остановился'
        ),
    )
    rejected_detail = models.TextField(
        'Причина отказа в проведении платежа',
        null=True,
        blank=True,
        help_text='Человекочитаемая ошибка платежа (для отображения клиенту)',
    )

    def __str__(self):
        return str(self.id)

