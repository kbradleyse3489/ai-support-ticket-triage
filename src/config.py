"""Fixed BEFORE evaluation: task taxonomy, operating policy, and reproducibility."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SEED = 42
VALIDATION_FRACTION = 0.2
MAX_INPUT_CHARS = 5000
MAX_VALIDATION_ERROR = 0.05
MIN_ACCEPTED_VALIDATION = 100
MIN_MARGIN = 0.10
MIN_KNOWN_TERMS = 2

# Project-defined operational queues. These are not labels supplied by BANKING77.
# Intents are mapped semantically, a priori, not learned from test performance.
QUEUE_INTENTS = {
    'Card lifecycle': [
        'card_arrival','card_linking','card_delivery_estimate','getting_virtual_card',
        'get_physical_card','visa_or_mastercard','disposable_card_limits','getting_spare_card',
        'order_physical_card','get_disposable_virtual_card','activate_my_card','card_about_to_expire'],
    'Card payments': [
        'card_payment_wrong_exchange_rate','extra_charge_on_statement','card_not_working',
        'contactless_not_working','card_payment_fee_charged','card_acceptance','pending_card_payment',
        'declined_card_payment','transaction_charged_twice','reverted_card_payment?',
        'virtual_card_not_working','apple_pay_or_google_pay'],
    'Top ups and deposits': [
        'automatic_top_up','top_up_by_bank_transfer_charge','pending_top_up','top_up_limits',
        'supported_cards_and_currencies','top_up_reverted','balance_not_updated_after_cheque_or_cash_deposit',
        'topping_up_by_card','top_up_by_cash_or_cheque','top_up_failed',
        'balance_not_updated_after_bank_transfer','top_up_by_card_charge'],
    'Transfers': [
        'cancel_transfer','transfer_not_received_by_recipient','declined_transfer','pending_transfer',
        'transfer_timing','beneficiary_not_allowed','transfer_fee_charged','receiving_money',
        'failed_transfer','transfer_into_account'],
    'Cash and ATMs': [
        'pending_cash_withdrawal','wrong_amount_of_cash_received','atm_support',
        'declined_cash_withdrawal','card_swallowed','wrong_exchange_rate_for_cash_withdrawal',
        'cash_withdrawal_charge'],
    'Account access and profile': [
        'age_limit','pin_blocked','edit_personal_details','passcode_forgotten','terminate_account','change_pin'],
    'Identity verification': [
        'why_verify_identity','unable_to_verify_identity','verify_source_of_funds','verify_top_up','verify_my_identity'],
    'Foreign exchange and coverage': [
        'exchange_rate','fiat_currency_support','exchange_via_app','exchange_charge','country_support'],
    'Security and disputes': [
        'lost_or_stolen_card','card_payment_not_recognised','compromised_card',
        'direct_debit_payment_not_recognised','lost_or_stolen_phone','request_refund',
        'Refund_not_showing_up','cash_withdrawal_not_recognised'],
}
INTENT_TO_QUEUE = {intent: queue for queue, intents in QUEUE_INTENTS.items() for intent in intents}
assert len(INTENT_TO_QUEUE) == 77
