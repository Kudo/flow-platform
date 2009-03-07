from django.shortcuts import render_to_response
import flowBase

def home(request):
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    
    return render_to_response('homepage.html', template_values)
