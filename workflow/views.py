from django.shortcuts import render_to_response, get_object_or_404
from workflow.models import Customer
from reportlab.pdfgen import canvas
from django.http import HttpResponse
#from rlextra.rml2pdf import rml2pdf
#import cStringIO
import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from cgi import escape
from django.http import HttpRequest
from workflow.models import Action
from django.db.models import Count,Sum
from datetime import timedelta
import datetime
from decimal import Decimal
from workflow.models import Invoice
from workflow.models import Customer
from django.http import HttpResponseRedirect

def render_to_pdf(template_src, context_dict,invnr):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+invnr+'.pdf'
        return response
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def print_invoice(request):
    if request.GET.get('invoice'):
        inv = Invoice.objects.get(id=request.GET.get('invoice'))
        cstm = Customer.objects.get(id=inv.customer.pk)

    invpos =  Action.objects.filter(invoice=inv).order_by('date_finished')

    net = 0
    tax = 0
    gross = 0

    invnr = inv.invoicenr

    for ps in invpos:
		
        dur = Decimal(ps.duration.seconds) / Decimal(3600)
        durext = Decimal(ps.duration_extern.seconds) / Decimal(3600)

        if (dur != durext) and (durext > 0):
            net += Decimal(durext) * Decimal(ps.price)
            tax += (Decimal(durext) * Decimal(ps.price)* (Decimal(ps.tax) / Decimal(100)))
            gross += (Decimal(durext) * Decimal(ps.price)* (Decimal(ps.tax) / Decimal(100) + Decimal(1)))

			
        else:
            net += Decimal(dur) * Decimal(ps.price)
            tax += (Decimal(dur) * Decimal(ps.price)* (Decimal(ps.tax) / Decimal(100)))
            gross += (Decimal(dur) * Decimal(ps.price)* (Decimal(ps.tax) / Decimal(100) + Decimal(1)))


	"""Format to two Pos after comma"""
		
    net = ('%.2f' % (Decimal(net))).replace('.', ',')
    tax = ('%.2f' % (Decimal(tax))).replace('.', ',')
    gross = ('%.2f' % (Decimal(gross))).replace('.', ',')
    today = datetime.date.today()
    today = today.strftime("%d.%m.%Y")
    if inv.description:
        escpdescr = inv.description
        escpdescr.replace('\n', '<br />')
    else:
        escpdescr = ""
    return render_to_pdf(
            'invoice.html',
            {
                'pagesize':'A4',
                'address_name': cstm.name,
                'address_add': inv.customeradd,
                'address_street': cstm.street,
                'address_postal': cstm.postal,
                'address_city': cstm.city,
                'invoicename':inv.name,
                'today' : today,
                'poslist': invpos,
                'invoicenr': inv.invoicenr,
                'net': net,
                'tax':tax,
                'gross' : gross,
                'description': inv.description
                
            },
            invnr
        )	

def remove_pos_from_invoice(request):
	if request.GET.get('pos'):	
		pos = Action.objects.get(id=request.GET.get('pos'))
		pos.invoice = None
		pos.billed = False
		pos.save()
		pos.project.billed = False
		pos.project.save()
		return HttpResponseRedirect("/workflow/invoice/%s/" % request.GET.get('inv'))	

def kunden(request):
    #customers_list = Customer.objects.all().order_by('name')[:5]
    #return render_to_response('workflow/index.html',{'customers_list': customers_list})
   #myvals = ""
	invnr = "R0324345345"
	myvals =  Action.objects.filter(project=request.GET.get('project')).filter(billed=0)
     #   myvals +=e.name + ','
 #   return render_to_response('workflow/kunden.html',{'customers_list': myvals})

		#~ # Create the HttpResponse object with the appropriate PDF headers.
		#~ response = HttpResponse(mimetype='application/pdf')
		#~ response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
#~ 
		#~ # Create the PDF object, using the response object as its "file."
		#~ myvals = ""
		#~ for e in Customer.objects.all():
			#~ myvals +=e.name + ','
		#~ p = canvas.Canvas(response)
		#~ 
		#~ # Draw things on the PDF. Here's where the PDF generation happens.
		#~ # See the ReportLab documentation for the full list of functionality.
		#~ p.drawString(100, 100, "Hello world." + myvals)
#~ 
		#~ # Close the PDF object cleanly, and we're done.
		#~ p.showPage()
		#~ p.save()
		#~ return response
		#~ rml = getRML(request)
		#~ buf = cStringIO.StringIO()
		#~ rml2pdf.go(rml, outputFileName=buf)
		#~ buf.reset()
		#~ pdfData = buf.read()
		#~ response = HttpResponse(mimetype='application/pdf')
#~ 
#~ 
		#~ response.write(pdfData)
		#~ response['Content-Disposition'] = 'attachment; filename=output.pdf'
		#~ return response
    #Retrieve data or whatever you need
	results = myvals
	return render_to_pdf(
            'mytemplate.html',
            {
                'pagesize':'A4',
                'mylist': myvals,
            },
            invnr
        )




def detail(request, customer_id):
    p = get_object_or_404(Customer,pk=customer_id)
    return render_to_response('workflow/detail.html', {'customer': p})

def results(request, customer_id):
    return HttpResponse("You're looking at the results of customer %s." % customer_id)
