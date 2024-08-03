"""Signals."""
from blinker import Namespace
my_signals = Namespace()

audittrail_signals = my_signals.signal('auditrail_log')
logon_logs = my_signals.signal('logon_log')