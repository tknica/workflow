# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from durationfield.db.models.fields.duration import DurationField
import datetime
# Customer

class Customer (models.Model):
	name = models.CharField( max_length=200 )
	street = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Straße' )
	postal = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Postleitzahl' )
	city = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Stadt' )
	telephone = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Telefon' )
	telefax = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Telefax' )
	email = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'E-Mail' )
	contact = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Ansprechpartner' )
	price = models.DecimalField(max_digits=12, decimal_places=2,default="60.00",verbose_name = 'Preis')
	tax = models.IntegerField( max_length=5 ,default="19",verbose_name = 'Steuer')	
	description = models.TextField( null=True, blank=True, verbose_name = 'Notiz')
	date_created = models.DateTimeField( auto_now_add = True, verbose_name = 'Erstellt am' )
	date_modified = models.DateTimeField( auto_now = True, verbose_name = 'Geändert am' )
	created_by = models.ForeignKey( User, related_name = 'customer_created', null=True, blank=True, verbose_name = 'Erstellt von' )
	modified_by = models.ForeignKey( User, related_name = 'customer_modified', null=True, blank=True, verbose_name = 'Geändert von' )

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = "Kunde"
		verbose_name_plural = "Kunden"		



# Project

class ProjectCategory (models.Model):
	name = models.CharField( max_length=200 )

	class Meta:
		verbose_name = 'Projektkategorie'
		verbose_name_plural = 'Projektkategorien'

	def __unicode__(self):
		return self.name



class Project (models.Model):
	name = models.CharField( max_length=200 )
	customer = models.ForeignKey( Customer, verbose_name = 'Kunde' )
	projectcategory = models.ForeignKey(ProjectCategory, verbose_name = 'Projektkategorie' )
	employees = models.ManyToManyField( User, related_name = 'project_employees', verbose_name = 'Mitarbeiter' )
	done = models.BooleanField(verbose_name = 'Fertig')
	billed = models.BooleanField(verbose_name = 'Abgerechnet')
	deadline_extern = models.DateTimeField(verbose_name = 'Externe Deadline', null=True, blank=True )
	deadline_intern = models.DateTimeField(verbose_name = 'Interne Deadline', null=True, blank=True )
	description = models.TextField( null=True, blank=True, verbose_name = 'Notiz')
	date_created = models.DateTimeField( auto_now_add = True, verbose_name = 'Erstellt am' )
	date_modified = models.DateTimeField( auto_now = True, verbose_name = 'Geändert am' )
	created_by = models.ForeignKey( User, related_name = 'project_created', null=True, blank=True, verbose_name = 'Erstellt von' )
	modified_by = models.ForeignKey( User, related_name = 'project_modified', null=True, blank=True, verbose_name = 'Geändert von' )

	def get_employees(self):
		return '%s' % (', '.join(a.username for a in self.employees.all()))
	get_employees.short_description = 'Zugeordnete Mitarbeiter'

	def __unicode__(self):
		return self.name

	def selflink(self):
		
		if self.id:
			return "<a href='/workflow/project/%s' target='_blank'>%s</a>" % (str(self.id), str(self.name))
		else:
			return "Not present"
	
	selflink.allow_tags = True
	selflink.short_description = 'Projekt'

	class Meta:
		verbose_name = "Projekt"
		verbose_name_plural = "Projekte"



# Action

class ActionStatus (models.Model):
	name = models.CharField( max_length=200 )

	class Meta:
		verbose_name = 'Bearbeitungszustand'
		verbose_name_plural = 'Bearbeitungszustände'

	def __unicode__(self):
		return self.name



def get_status():
	return ActionStatus.objects.get(id=1)



class ActionCategory (models.Model):
	name = models.CharField( max_length=200 )

	class Meta:
		verbose_name = 'Aktionskategorie'
		verbose_name_plural = 'Aktionskategorien'

	def __unicode__(self):
		return self.name

class InvoiceStatus (models.Model):
	name = models.CharField( max_length=200 )

	class Meta:
		verbose_name = 'Rechnungszustand'
		verbose_name_plural = 'Rechnungszustände'

	def __unicode__(self):
		return self.name


def get_invoice_status():
	return InvoiceStatus.objects.get(id=1)

class Invoice (models.Model):
	invoicenr = models.CharField( max_length=20,verbose_name = 'Rechnungsnummer' )
	invoicedate = models.DateTimeField(verbose_name = 'Rechnungsdatum', default=datetime.date.today )
	name = models.CharField( max_length=200 )
	project = models.ForeignKey( Project, verbose_name = 'Projekt' )
	customer = models.ForeignKey( Customer, verbose_name = 'Kunde' )
	customeradd = models.CharField( max_length=200, null=True, blank=True, verbose_name = 'Adresszusatz' )
	invoicestatus = models.ForeignKey( InvoiceStatus, verbose_name = 'Rechnungszustand', default=get_invoice_status )	
	description = models.TextField( null=True, blank=True, verbose_name = 'Notiz')
	date_created = models.DateTimeField( auto_now_add = True, verbose_name = 'Erstellt am'  )
	date_modified = models.DateTimeField( auto_now = True, verbose_name = 'Geändert am' )
	created_by = models.ForeignKey( User, related_name = 'invoice_created', null=True, blank=True, verbose_name = 'Erstellt von' )
	modified_by = models.ForeignKey( User, related_name = 'invoice_modified', null=True, blank=True, verbose_name = 'Geändert von' )

	def __unicode__(self):
		return "%s" % (self.invoicenr)

	def selflink(self):
		
		if self.id:		
			today = datetime.date.today()
			year = today.strftime("%y")
			return "<a href='/workflow/invoice/%s' target='_self'>%s</a>" % (self.id,self.invoicenr)
		else:
			return "Not present"
	
	selflink.allow_tags = True
	selflink.short_description = 'Rechnung'

class Action (models.Model):
	name = models.CharField( max_length=200 )
	project = models.ForeignKey( Project, verbose_name = 'Projekt' )
	invoice = models.ForeignKey( Invoice, verbose_name = 'Rechnung', null=True, blank=True,on_delete=models.SET_NULL)
	actionstatus = models.ForeignKey(ActionStatus, verbose_name = 'Bearbeitungszustand', default=get_status )
	actioncategory = models.ForeignKey(ActionCategory, verbose_name = 'Aktionskategorie' )
	owner = models.ForeignKey( User, related_name = 'action_owner', null=True, blank=True, verbose_name = 'Bearbeitet von' )
	done = models.BooleanField(verbose_name = 'Fertig')
	billed = models.BooleanField(verbose_name = 'Abgerechnet')
	price = models.DecimalField(max_digits=12, decimal_places=2,verbose_name = 'Preis')
	tax = models.IntegerField( max_length=5 ,verbose_name = 'Steuer')
	duration = DurationField(default="0:00",verbose_name = 'Dauer')
	duration_extern = DurationField(default="0:00",verbose_name = 'Dauer in Rechn.')
	date_finished = models.DateTimeField(verbose_name = 'Fertiggestellt', null=True, blank=True )
	deadline_extern = models.DateTimeField(verbose_name = 'Externe Deadline', null=True, blank=True )
	deadline_intern = models.DateTimeField(verbose_name = 'Interne Deadline', null=True, blank=True )
	description = models.TextField( null=True, blank=True, verbose_name = 'Notiz')
	date_created = models.DateTimeField( auto_now_add = True, verbose_name = 'Erstellt am'  )
	date_modified = models.DateTimeField( auto_now = True, verbose_name = 'Geändert am' )
	created_by = models.ForeignKey( User, related_name = 'action_created', null=True, blank=True, verbose_name = 'Erstellt von' )
	modified_by = models.ForeignKey( User, related_name = 'action_modified', null=True, blank=True, verbose_name = 'Geändert von' )

	def customer(self):
		return self.project.customer
	customer.short_description = 'Customer'
	
	def index(self):
		return "test"


	def add(self):
		return "<a href='/workflow/action/%s' target='_blank'>%s</a>" % (self.id, self.name)
		
		
	def selflink(self):
		
		if self.id:
			return u"<a href='/workflow/action/%s/?project=%s' target='_blank'>%s</a>" % (self.id, self.project.pk, self.name)
		else:
			return "Not present"
	
	selflink.allow_tags = True
	selflink.short_description = 'Aktion'	

	def edit(self):
		
		if self.id:
			return "<a href='/workflow/action/%s' target='_blank'>%s</a>" % (str(self.id), "Bearbeiten")
		else:
			return "Nicht vorhanden"

	edit.allow_tags = True
	edit.short_description = 'Aktion'

	def get_remove_invoice_pos_link(self):
		return u"<a class='delete_pos_link' href='/remove_pos_from_invoice?inv=%s&pos=%s'>Position entfernen</a>" %  (self.invoice.pk,self.id)

	get_remove_invoice_pos_link.allow_tags = True
	get_remove_invoice_pos_link.short_description = 'Entfernen'

	def non_editable_date_finished(self):
		return u"%s" %  (self.date_finished)

	non_editable_date_finished.short_description = 'Fertiggestellt'

	def non_editable_duration(self):
		return u"%s" %  (self.duration)

	non_editable_duration.short_description = 'Dauer'



	# Bearbeitungszustand auf Abgeschlossen ( pk = 2 ) setzen, wenn Feld Fertig gesetzt

	def save(self, *args, **kwargs):
		if self.done == True:
			status = ActionStatus.objects.get(pk='2')
			self.actionstatus = status
		if self.actionstatus.pk == 2:
			self.done = 1
		super(Action, self).save(*args, **kwargs)



	class Meta:
		verbose_name = 'Aktion'
		verbose_name_plural = 'Aktionen'

	def __unicode__(self):
		return self.name


		

