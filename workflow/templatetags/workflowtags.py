from django import template
from django.template.defaultfilters import stringfilter
from datetime import timedelta

#
#from django.db import models
#from django.db.models.fields.subclassing import SubfieldBase
from decimal import Decimal


register = template.Library()

@register.filter
def get_amount(duration, duration_extern):
	
	dur = Decimal(duration.seconds) / Decimal(3600)
	durext = Decimal(duration_extern.seconds) / Decimal(3600)
	
	if (dur != durext) and (durext > 0):
		return durext
	else:
		return dur


@register.filter
def get_sum(duration, price):
	return ('%.2f' % (Decimal(duration) * Decimal(price))).replace('.', ',')

