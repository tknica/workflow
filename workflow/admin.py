# -*- coding: utf-8 -*-
from workflow.models import Customer
from workflow.models import ProjectCategory
from workflow.models import Project
from workflow.models import ActionStatus
from workflow.models import ActionCategory
from workflow.models import Action
from workflow.models import InvoiceStatus
from workflow.models import Invoice
from django.forms import models 
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count,Sum
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from datetime import timedelta
from django.http import HttpRequest
import datetime
from datetime import datetime
from datetime import date
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.forms.models import BaseInlineFormSet
from django import forms
from django.forms import ModelForm
from django.forms import ModelChoiceField
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
import time, locale
locale.setlocale(locale.LC_ALL, '')


# CustomerAdmin model

class CustomerAdmin(admin.ModelAdmin):
	readonly_fields = ['date_created','created_by','date_modified','modified_by']
	ordering = ['name']
	fieldsets = (
		('Kundendaten',
			{
				'fields': 
					( 'name', 'street', 'postal','city', 'telephone', 'telefax', 'email', 'contact','price','tax','description' )
			}
		),	
		('Info',
			{
				'fields': 
					('date_created','created_by','date_modified','modified_by')
			}
		),
	)

	list_display = ('related_projects','get_changelink')
	
	
	def related_projects(self, obj):
		from django.core import urlresolvers
		url = urlresolvers.reverse("admin:workflow_project_changelist")
		lookup = u"customer"
		text = obj.name
		return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)

	related_projects.allow_tags = True
	related_projects.short_description = 'Kunde'

	def get_changelink(self, obj):
		return u"<a class='changelink' href='/workflow/customer/%s'>&Auml;ndern</a>" %  (obj.pk)

	get_changelink.allow_tags = True
	get_changelink.short_description = 'Bearbeiten'


	def save_model(self, request, obj, form, change):
		instance = form.save(commit=False)
		instance.created_by = request.user
		instance.modified_by = request.user
		instance.save()
		return instance


##############################
###### Project Category ######
##############################

class ProjectCategoryAdmin(admin.ModelAdmin):

	list_display = ('name',)


#################################
###### Project Change List ######
#################################

class ProjectChangeList(ChangeList):
	def get_results(self, request, *args, **kwargs):
		super(ProjectChangeList, self).get_results(request, *args, **kwargs)
		#q = self.result_list.aggregate(action_sum=Sum('deadline_extern'))
		#self.action_count = q['action_sum']
		if request.GET.get('customer'):
			cstm = Customer.objects.get(id=request.GET.get('customer'))
			self.customername = cstm.name
		else:
			self.customername = "Alle Projekte"


#####################
###### Project ######
#####################		

class ProjectAdmin(admin.ModelAdmin):

	readonly_fields = ['date_created','created_by','date_modified','modified_by']
	ordering = ['name']
	fieldsets = (
		('Projektdaten',{
				'fields': ( 'name','customer','projectcategory', 'employees','done','billed','deadline_extern', 'deadline_intern','description' )
		}),
		('Info',{
				'fields': ('date_created','created_by','date_modified','modified_by')
		}),		

	)

	list_display = ('related_actions','projectcategory', 'get_employees','done','billed','date_created', 'deadline_extern', 'deadline_intern','description','get_changelink' )
	search_fields = ['name']

	def get_changelist(self, request):
		return ProjectChangeList


	def related_actions(self, obj):
		from django.core import urlresolvers
		url = urlresolvers.reverse("admin:workflow_action_changelist")
		lookup = u"project"
		text = obj.name
		return u"<a href='%s?%s=%d'>%s</a>" % (url, lookup, obj.pk, text)


	related_actions.allow_tags = True
	related_actions.short_description = 'Projekte'

	def get_changelink(self, obj):
		return u"<a class='changelink' href='/workflow/project/%s'>&Auml;ndern</a>" %  (obj.pk)

	get_changelink.allow_tags = True
	get_changelink.short_description = 'Bearbeiten'

	def response_add(self, request, obj, post_url_continue=None):
		from django.http import HttpResponseRedirect
		url = "/workflow/project/?customer=%s" % (obj.customer.pk)
		return HttpResponseRedirect(url)

	def save_model(self, request, obj, form, change):
		instance = form.save(commit=False)
		instance.created_by = request.user
		instance.modified_by = request.user
		instance.save()
		return instance


################################
###### Action Change List ######
################################

#class ActionChangeList(ChangeList):
#	def get_results(self,request, *args, **kwargs):
#		super(ActionChangeList, self).get_results(request, *args, **kwargs)
#		#q = self.result_list.aggregate(action_sum=Sum('duration'))
#		#self.action_count = timedelta(microseconds=q['action_sum'])
#		if request.GET.get('project'):
#			prj = Project.objects.get(id=request.GET.get('project'))
#			cstm = Customer.objects.get(id=prj.customer.pk)
#			self.projectname = cstm.name + " - " + prj.name
#		else:
#			self.projectname = "Alle Aktionen"


###########################
###### Action Status ######
###########################
			
class ActionStatusAdmin(admin.ModelAdmin):

	list_display = ('name',)


#################################
###### ActionCategoryAdmin ######
#################################

class ActionCategoryAdmin(admin.ModelAdmin):

	list_display = ('name',)


###########################
###### ByMonthFilter ######
###########################

class ByMonthFilter(SimpleListFilter):
	title = _('Aktionen per Monat')

	parameter_name = 'month'

	def lookups(self, request, model_admin):

		first_act = Action.objects.filter(date_finished__gte=date(2010,1,1)).order_by('date_finished')[0]
		last_act = Action.objects.filter(date_finished__gte=date(2010,1,1)).order_by('-date_finished')[0]

		current_year = first_act.date_finished.year

		#Get years
		years_cnt = last_act.date_finished.year - first_act.date_finished.year
			
		month_list = []
			
		for yr in range(0,(years_cnt+1)):
				
			# set first month to january
			start_month = 1
			end_month = 13
				
			if yr == 0:
				# set first month to month of first action for first year
				start_month = first_act.date_finished.month
				
			if yr == years_cnt:
				# set end month to month of last action for the latest year
				end_month = last_act.date_finished.month +1

				
			for mth in range(start_month,end_month):
				month_list.append((date(current_year,mth,1),_(date(current_year,mth,1).strftime('%B') + " " + str(current_year))))
			current_year = current_year + 1
			
			month_list.append(("notready",_("nicht fertig")))
		return (month_list)

		
	def queryset(self, request, queryset):
		if self.value() == "notready":
			return queryset.filter(date_finished=None)
		if self.value() != None:
			selected_month = self.value()
			sel_date = datetime.strptime(selected_month,'%Y-%m-%d')
			return queryset.filter(date_finished__gte=date(int(sel_date.strftime('%Y')),int(sel_date.strftime('%m')),1),
							date_finished__lte=date(int(sel_date.strftime('%Y')),int(sel_date.strftime('%m')) +1,1))
 

#####################################
###### ProjectModelChoiceField ######
#####################################

class ProjectModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Return a string of the format: "firstname lastname (username)"
        return "%s   -->  %s"%(obj.customer.name, obj.name)


#############################
###### ActionAdminForm ######
#############################

class ActionAdminForm(ModelForm):
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(ActionAdminForm, self).__init__(*args, **kwargs)
		if self.request.GET.get('project'):
			prj = Project.objects.get(id=self.request.GET.get('project'))
			self.fields["project"].queryset = Project.objects.filter(customer = prj.customer).order_by('name')
		else:
			self.fields["project"] = ProjectModelChoiceField(Project.objects.all().order_by('customer__name'))

	class Meta:
		model = Action


#########################
###### ActionAdmin ######
#########################

class ActionAdmin(admin.ModelAdmin):
	readonly_fields = ['date_created','created_by','date_modified','modified_by','billed','duration_extern']
	fieldsets = (
		('Aktionsdaten',{
				'fields': ('name','project','actionstatus','actioncategory','owner','done','billed','active','duration','date_finished', 'deadline_extern', 'deadline_intern','description')
		}),
		('Info',{
				'fields': ('date_created','created_by','date_modified','modified_by')
		}),
	)

	list_display = ('selflink','id','invoice','actionstatus','actioncategory','owner','done','billed','active','duration','date_finished', 'deadline_extern', 'deadline_intern','description','get_changelink')
	list_filter = ('owner','billed','active',ByMonthFilter)

	actions = ['bill_it','add_actions_to_invoice','mark_as_ready','deactivate_actions']

	form = ActionAdminForm
	
	change_list_template = 'admin/workflow/extras/custom_changelist.html'

	def get_total(selfself,request):

		#filtervalues = []
		#if request.GET.has_key('project'):
		#	filtervalues.append("project=%s" % request.GET.get('project'))
			
		#if request.GET.has_key('owner__id__exact'):
		#	filtervalues.append("owner=%s" % request.GET.get('owner__id__exact'))
	
		#if request.GET.has_key('active__exact'):
		#	filtervalues.append("active=%s" % request.GET.get('active__exact'))
		
		#if request.GET.has_key('month'):
		#	filtervalues.append("active=%s" % request.GET.get('month'))
				
		#if request.GET.has_key('billed__exact'):
		#	filtervalues.append("billed=%s" % request.GET.get('billed__exact'))

		my_filter = {}
		if request.GET.has_key('project'):
			my_filter["project"] = request.GET.get('project')

		if request.GET.has_key('owner__id__exact'):
			my_filter["owner"] = request.GET.get('owner__id__exact')
	
		if request.GET.has_key('active__exact'):
			my_filter["active"] = request.GET.get('active__exact')
		
		if request.GET.has_key('month'):
			if request.GET.get('month') == "notready":
				my_filter["date_finished"] = None
			else:
				if request.GET.get('month') != None :
					sel_date = datetime.strptime(request.GET.get('month'),'%Y-%m-%d')
					my_filter["date_finished__gte"] = date(int(sel_date.strftime('%Y')),int(sel_date.strftime('%m')),1)
					my_filter["date_finished__lte"] = date(int(sel_date.strftime('%Y')),int(sel_date.strftime('%m')) +1,1)
				
		if request.GET.has_key('billed__exact'):
			my_filter["billed"] = request.GET.get('billed__exact')		

		
		q = Action.objects.filter(**my_filter).aggregate(tot=Sum('duration'))
		#q = Action.objects.all().aggregate(tot=Sum('duration'))
		if q['tot'] != None:
			total = timedelta(microseconds=q['tot'])
			#hours, remainder = divmod(total, 3600)
			#minutes, seconds = divmod(remainder, 60)
			#duration_formatted = '%s:%s:%s' % (hours, minutes, seconds)
			#scds = int(q / 1000000)
			days = total.days * 24
			hours =  int(time.strftime("%H",time.gmtime(total.seconds))) + days
			minutes = time.strftime("%M",time.gmtime(total.seconds))
			formated_duration = "%s:%s" % (hours,minutes)
		else:
			formated_duration = ""
		return formated_duration

	def changelist_view(self, request, extra_context=None):

		my_context = {
			'total': self.get_total(request),
		}
		
		if not request.GET.has_key('active__exact'):
			q = request.GET.copy()
			q['active__exact'] = '1'
			request.GET = q
			request.META['QUERY_STRING'] = request.GET.urlencode()
		return super(ActionAdmin,self).changelist_view(request, extra_context=my_context)

	# get_form method is needed to override the form

	def get_form(self, request, obj=None, **kwargs):
		AdminForm = super(ActionAdmin, self).get_form(request, obj, **kwargs)

		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass


	# Method to get a edit/change link in List

	def get_changelink(self, obj):
		return u"<a class='changelink' href='/workflow/action/%s'>&Auml;ndern</a>" %  (obj.pk)

	get_changelink.allow_tags = True
	get_changelink.short_description = 'Bearbeiten'


	# Override ActionAdmin save method

	def save_model(self, request, obj, form, change):
		instance = form.save(commit=False)
		instance.created_by = request.user
		instance.modified_by = request.user
		instance.owner = instance.owner
		if instance.owner is None:
			instance.owner = request.user
		if instance.billed == True:
			acts = Action.objects.filter(project=instance.project)
			not_billed = 0
			for act in acts:
				if act.billed == False and act.pk != instance.pk:
					not_billed = 1
			if not_billed == 0:
				instance.project.billed = True
				instance.project.save()
		else:
			if instance.project.billed == True:
				instance.project.billed = False
				instance.project.save()
						
		if instance.done == True:
			acts = Action.objects.filter(project=instance.project)
			not_done = 0
			for act in acts:
				if act.done == False and act.pk != instance.pk:
					not_done = 1
			if not_done == 0:
				instance.project.done = True
				instance.project.save()
		else:
			if instance.project.done == True:
				instance.project.done = False
				instance.project.save()

		if not instance.price:
			instance.price = instance.project.customer.price

		if not instance.tax:
			instance.tax = instance.project.customer.tax

		instance.save()
		return instance

	# Override ActionAdmin actions. Remove bill_it from actions .... if	

	def get_actions(self, request):
		actions = super(ActionAdmin, self).get_actions(request)
		if (request.GET.get('project') == None) or (request.GET.get('billed__exact') == "1" ):
			if 'bill_it' in actions:
				del actions['bill_it']
		return actions


	# Override Action response and redirect to related project page

	def response_add(self, request, obj, post_url_continue=None):
		from django.http import HttpResponseRedirect
		url = "/workflow/action/?project=%s" % (obj.project.pk)
		return HttpResponseRedirect(url)

	def response_change(self, request, obj, post_url_continue=None):
		from django.http import HttpResponseRedirect
		url = "/workflow/action/?project=%s" % (obj.project.pk)
		return HttpResponseRedirect(url)

	def response_delete(self, request, obj, post_url_continue=None):
		from django.http import HttpResponseRedirect
		url = "/workflow/action/?project=%s" % (obj.project.pk)
		return HttpResponseRedirect(url)


	# Creates a new invoice from choosed actions, if all choosed actions are done, not billed, means don't belong already to another invoice
			
	def bill_it (self, request, queryset):
		already_in_invoice = 0
		not_done = 0
		notices = ""
		for obj in queryset:
			if obj.invoice:
				already_in_invoice = 1
				notices += "<br />#" + str(obj.pk) + " " + obj.name + " ist schon Rechnung " + obj.invoice.invoicenr + " zugeordnet!"
			if obj.done == False:
				not_done = 1
				notices += "<br />#" + str(obj.pk) + " " + obj.name + " ist nicht abgeschlossen!"
		if already_in_invoice == 0 and not_done == 0:
			invoice_id = make_new_invoice(request.GET.get('project'))
			queryset.update( billed = 1, invoice = invoice_id )
			prj = Project.objects.get(id=request.GET.get('project'))
			acts = Action.objects.filter(project=prj)
			not_billed = 0
			actsn = ""
			for act in acts:
				if act.billed == False:
					not_billed = 1
			if not_billed == 0:
				prj.billed = True
				prj.save()
			message = "Rechnung erstellt"
			messages.success(request, "%s" % message)
		else:
			message = "Rechnung kann nicht erstellt werden."	
			messages.error(request, "%s%s" % (message,notices), extra_tags='safe')
	
	bill_it.short_description = "Rechnung erstellen"

	def mark_as_ready (self, request, queryset):
		for obj in queryset:
			obj.done = True
			actstat = ActionStatus.objects.get(id=2)
			obj.actionstatus = actstat
			obj.save()
		message = "Gewählte Aktionen als fertig markiert."
		messages.success(request, "%s" % message, extra_tags='safe')
	
	mark_as_ready.short_description = "Aktionen als fertig markieren"


	def deactivate_actions (self, request, queryset):
		for obj in queryset:
			obj.active = False
			obj.save()
		message = "Gewählte Aktionen deaktiviert."
		messages.success(request, "%s" % message, extra_tags='safe')
	deactivate_actions.short_description = "Aktionen deaktivieren"


	def add_actions_to_invoice(self, request, queryset):
		if request.POST.get('post'):
			if request.POST.get('invoices'):
				inv = Invoice.objects.get(id=request.POST.get('invoices'))
				already_in_invoice = 0
				not_done = 0
				notices = ""
				for obj in queryset:
					if obj.invoice:
						already_in_invoice = 1
						notices += "<br />#" + str(obj.pk) + " " + obj.name + " ist schon Rechnung " + obj.invoice.invoicenr + " zugeordnet!"
					if obj.done == False:
						not_done = 1
						notices += "<br />#" + str(obj.pk) + " " + obj.name + " ist nicht abgeschlossen!"

				if already_in_invoice == 0 and not_done == 0:
					for obj in queryset:
						obj.invoice = inv
						obj.billed = True
						obj.save()

					
					not_billed = 0
					acts = Action.objects.filter(project=inv.project)
					for act in acts:
						if act.billed == False:
							not_billed = 1
					if not_billed == 0:
						inv.project.billed = True
						inv.project.save()
					messages.success(request, "Aktionen wurden zu %s hinzugef&uuml;gt." % inv.invoicenr, extra_tags='safe')
				else:
					message = "Aktionen k&ouml;nnen nicht hinzugef&uuml;gt werden."	
					messages.error(request, "%s%s" % (message,notices), extra_tags='safe')

		else:
			prj = Project.objects.get(id=request.GET.get('project'))
			invoices = Invoice.objects.filter(project=prj)
			context = {
				'invoices':invoices,
                'title': ("Rechnung auswählen"),
                'queryset': queryset,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }
			return TemplateResponse(request, 'admin/invoice_form.html',context, current_app=self.admin_site.name)

	add_actions_to_invoice.short_description = 'Aktionen zu Rechnung hinzufügen'


#################################
###### ActionInlineFormset ######
#################################
        
#class ActionInlineFormset(forms.models.BaseInlineFormSet):
#	can_delete = False
#	def clean(self):
#		cleaned_data = self.cleaned_data
#		delete_checked = False
#		for form in self.forms:
#			try:
#				if form.cleaned_data:
#					#getid = form.cleaned_data['name']
#					#posis = Action.objects.get(pk=57)
#					#posis.update( name = "Hello Hello" )
#					if form.cleaned_data['DELETE']:
#						posis = form.cleaned_data['id']
#						#posis = Action.objects.get(pk=getid)
#						posis.invoice = None
#						posis.save()				
#						delete_checked = True

#			except AttributeError:
#				pass
				
#		if delete_checked:
#			raise forms.ValidationError(u'Action removed from invoice.')


##############################
###### ActionInlineForm ######
##############################

class ActionInlineForm(ModelForm):

	class Meta:
		model = Action
		fields = ['name','tax', 'price','duration_extern']


# ActionInline model

class ActionInline(admin.TabularInline):
	model = Action
	#formset = ActionInlineFormset
	form = ActionInlineForm
	extra = 0
	ordering = ('date_finished',)
	can_delete=False
	readonly_fields = ['non_editable_date_finished','non_editable_duration','get_remove_invoice_pos_link']


# InvoiceStatusAdmin model
			
class InvoiceStatusAdmin(admin.ModelAdmin):
	list_display = ('name',)   


# InvoiceAdmin model
 
class InvoiceAdmin(admin.ModelAdmin):
	fieldsets = (
		('Rechnungssdaten',{
				'fields': ('name','invoicenr','invoicedate','customer','customeradd','project','invoicestatus','description')
		}),
	)
	list_display = ('selflink','invoicestatus','name','customer','customeradd','project','get_printlink')
	inlines = [
        ActionInline,
    ]
	list_filter = ('invoicestatus','customer')
	actions = ['delete_model']
    
	def save_model(self, request, obj, form, change):	
		instance = form.save(commit=False)
		today = date.today()
		year = today.strftime("%y")

		if instance.invoicenr == "":
			try:
				last_invoices = Invoice.objects.filter(invoicenr__contains='R0'+year).order_by('-invoicenr')[0]
				#last_invoice = Invoice.objects.latest('id')

				if last_invoices:
				#currentyear = last_invoice.invoicenr[2:4]
				#if int(year) == int(currentyear): 
					currentnr = last_invoices.invoicenr[5:7] 
					currentnr = int(currentnr) + 1
					instance.invoicenr = "str(currentnr)"
				else:
					instance.invoicenr = "R%03d%03d" % (int(year),1)
			except Exception:
				instance.invoicenr = "R%03d%03d" % (int(year),1)
		else:
			instance.invoicenr = instance.invoicenr

		instance.save()
		return instance

	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		for instance in instances:
			usr = User.objects.get(id=7)
			try:
				instance.created_by = instance.created_by
			except:
				instance.created_by = usr

			try:
				instance.owner = instance.owner
			except:
				instance.owner = usr

			instance.modified_by = usr

			try:
				instance.date_created = instance.date_created
			except:
				instance.date_created = date.today()

			instance.date_modified = date.today()

			try:
				instance.project = instance.project
			except:
				pr = Project.objects.get(id=instance.invoice.project.id)
				instance.project = pr

			actstat = ActionStatus.objects.get(id=2)
			instance.actionstatus = actstat

			try:
				instance.actioncategory = instance.actioncategory
			except:
				cat = ActionCategory.objects.get(id=9)
				instance.actioncategory = cat

			instance.done = True
			instance.billed = True	
		 	instance.save()
		formset.save_m2m()

	def get_actions(self, request):
		actions = super(InvoiceAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions

	def delete_model(self, request, obj):
		for o in obj.all():
			Action.objects.filter(invoice=o).update(billed=False)
			o.delete()
			
	delete_model.short_description = 'Ausgewählte Rechnungen löschen'

	def get_printlink(self, obj):
		return u"<a class='printlink' href='/print_invoice?invoice=%s'>Rechnung drucken</a>" %  (obj.pk)

	get_printlink.allow_tags = True
	get_printlink.short_description = 'Drucken'


def make_new_invoice (project):		
	today = date.today()
	year = today.strftime("%y")
	prj = Project.objects.get( id = project )
		
	try:	
		last_invoice = Invoice.objects.filter(invoicenr__contains='R0'+year).order_by('-invoicenr')[0]
		currentyear = last_invoice.invoicenr[2:4]
		if int(year) == int(currentyear): 
			currentnr = last_invoice.invoicenr[4:7] 
			currentnr = int(currentnr) + 1						
			newinvoice = Invoice(invoicenr=("R%03d%03d" % (int(year),int(currentnr))),project=prj, customer=prj.customer,customeradd = "",name = prj.name)
		else:
			newinvoice = Invoice(invoicenr=("R%03d%03d" % (int(year),1)),project=prj, customer=prj.customer,customeradd = "",name = prj.name)
	except Exception:	
		newinvoice = Invoice(invoicenr=("R%03d%03d" % (int(year),1)),project=prj, customer=prj.customer,customeradd = "",name = prj.name)
	newinvoice.save()
	return newinvoice.id
		
admin.site.register(Customer,CustomerAdmin)
admin.site.register(ProjectCategory,ProjectCategoryAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(ActionStatus,ActionStatusAdmin)
admin.site.register(ActionCategory,ActionCategoryAdmin)
admin.site.register(InvoiceStatus,InvoiceStatusAdmin)
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Action,ActionAdmin)

#admin.site.unregister(User)
#admin.site.unregister(Group)
#admin.site.unregister(Project)
