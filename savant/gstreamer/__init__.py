"""GStreamer module."""

# ruff: skip-file
# to avoid `gi.require_version` warning
import gi  # noqa: F401

gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')

# pylint:disable=wrong-import-position
from gi.repository import GLib, GObject, Gst, GstApp, GstBase  # noqa: F401, E402

# mainstream patch #911: support PyGObject releases without range constructors.
try:
    Gst.Fraction(0, 1)
except TypeError:
    native_fraction = Gst.Fraction

    def fraction(numerator, denominator):
        value = native_fraction()
        value.num = numerator
        value.denom = denominator
        return value

    native_fraction.__str__ = lambda self: f'{self.num}/{self.denom}'
    Gst.Fraction = fraction

try:
    Gst.IntRange(range(1, 2))
except TypeError:
    native_int_range = Gst.IntRange

    def int_range(values):
        value = native_int_range()
        value.min = values.start
        value.max = values.stop - 1
        return value

    native_int_range.__str__ = lambda self: f'{self.min}..{self.max}'
    Gst.IntRange = int_range

try:
    Gst.FractionRange(Gst.Fraction(0, 1), Gst.Fraction(1, 1))
except TypeError:
    native_fraction_range = Gst.FractionRange

    def fraction_range(minimum, maximum):
        value = native_fraction_range()
        value.min = minimum
        value.max = maximum
        return value

    native_fraction_range.__str__ = lambda self: f'{self.min}..{self.max}'
    Gst.FractionRange = fraction_range
