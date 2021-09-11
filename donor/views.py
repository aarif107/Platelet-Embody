from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from platelet import forms as bforms
from platelet import models as bmodels

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.PlateletRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.PlateletRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.PlateletRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.PlateletRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def donate_platelet_view(request):
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            platelet_donate=donation_form.save(commit=False)
            platelet_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            platelet_donate.donor=donor
            platelet_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.PlateletDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            platelet_request=request_form.save(commit=False)
            platelet_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            platelet_request.request_by_donor=donor
            platelet_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    platelet_request=bmodels.PlateletRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':platelet_request})

