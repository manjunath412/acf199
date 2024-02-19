from django.http import Http404

from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
# Create your views here.
#from .models import reporting_period

from .forms import QuarterForm, MonthForm, FamilyForm
from .models import Quarter, Month, Family, Adult, Child


class QuarterListView(LoginRequiredMixin, ListView):
    model = Quarter
    context_object_name = "quarters"
    template_name = "section1/quarter_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class MonthListView(ListView):
    model = Month
    context_object_name = 'months'
    template_name = 'section1/month_list.html'
    
    def get_queryset(self):
        return Month.objects.filter(quarter_id=self.kwargs['quarter_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter = Quarter.objects.get(pk=self.kwargs['quarter_pk'])
        context['quarter'] = quarter 
        return context

class FamilyListView(ListView):
    model = Family
    context_object_name = 'families'
    template_name = 'section1/family_list.html'

    def get_queryset(self):
        return Family.objects.filter(month_id=self.kwargs['month_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = Month.objects.get(pk=self.kwargs['month_id'])
        context['month'] = month
        return context

class QuarterCreateView(LoginRequiredMixin, CreateView):
    model = Quarter
    form_class = QuarterForm
    context_object_name = "quarter"
    template_name = "section1/quarter_form.html"
    success_url = reverse_lazy('quarter-list')

    def get_success_url(self):
        return self.success_url

class MonthCreateView(CreateView):
    model = Month
    #form_class = MonthForm
    context_object_name = "month"
    fields = ['report_month', 'start_date', 'end_date']
    template_name = 'section1/month_form.html'

    def form_valid(self, form):
        form.instance.quarter = Quarter.objects.get(pk=self.kwargs['quarter_pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quarter'] = Quarter.objects.get(pk=self.kwargs['quarter_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('month-list', kwargs={'quarter_pk': self.kwargs['quarter_pk']})

class FamilyCreateView(LoginRequiredMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = 'section1/family_form.html'
    
    def form_invalid(self, form):
        print("Form is invalid")
        for field in form.errors:
            print("Error in field:", field)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        print("Form is valid")
        try:
            month_instance = Month.objects.get(pk=self.kwargs['month_id'])
            form.instance.month = month_instance
            form.instance.created_by_id = self.request.user.id
            form.instance.updated_by_id = self.request.user.id
        except Month.DoesNotExist:
            form.add_error('month', 'Invalid month specified!')
        
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Case Overview': ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                            'disposition', 'new_applicant', 'num_family_members', 'family_type', \
                            'receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                            'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            
            #'Benefits': ['receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
            #            'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            'TANF Assistance': ['item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'fam_exempt_fed_time_limits',\
                                'item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                                'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
                                'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
                                'item26c3_red_len_assist', 'item26c4_other_non_sanction'],
            #'Reductions': ['item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
            #                        'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
            #                            'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
            #                                'item26c3_red_len_assist', 'item26c4_other_non_sanction' ],
            'ControlFields': ['month', 'created_by', 'created_at', 'updated_by', 'updated_at']
            #'TANF Federal Time Limit Exemption': ['fam_exempt_fed_time_limits']
            }
        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'month_instance'):
            self.month_instance = Month.objects.get(pk=self.kwargs['month_id'])
        context['month'] = self.month_instance
        if 'form' in context:
            context['field_groups'] = context['form'].field_groups
        return context
    
    def get_success_url(self):
        return reverse_lazy('family_list', kwargs={'month_id': self.kwargs['month_id']})

class QuarterUpdateView(LoginRequiredMixin, UpdateView):
    model = Quarter
    fields = ['report_quarter', 'start_date', 'end_date']
    context_object_name = "quarter"
    template_name = "section1/quarter_update.html"
    success_url = reverse_lazy('quarter-list')

    def get_success_url(self):
        return self.success_url

class MonthUpdateView(LoginRequiredMixin, UpdateView):
    model = Month
    fields = ['report_month', 'start_date', 'end_date']
    context_object_name = "month"
    template_name = "section1/month_update.html"
    #success_url = reverse_lazy('month-list')

    def get_success_url(self):
        quarter_pk = self.object.quarter.id
        return reverse('month-list', kwargs={'quarter_pk': quarter_pk})

class FamilyUpdateView(UpdateView):
    model = Family
    form_class = FamilyForm
    context_object_name = "family"
    template_name = "section1/family_update.html"

    # Similar setup to FamilyCreateView
    def get_success_url(self):
        month_id = self.object.month_id
        return reverse('family_list', kwargs={'month_id': month_id})

    def get_form(self, form_class=None):
        form_class = super().get_form(form_class)
        form_class.field_groups = self.get_field_groups(form_class)
        return form_class

    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Case Overview': ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                            'disposition', 'new_applicant', 'num_family_members', 'family_type', \
                            'receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                            'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            
            #'Benefits': ['receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
            #            'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            'TANF Assistance': ['item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'fam_exempt_fed_time_limits'],
            'Reductions': ['item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                                    'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
                                        'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
                                            'item26c3_red_len_assist', 'item26c4_other_non_sanction' ],
            #'TANF Federal Time Limit Exemption': ['fam_exempt_fed_time_limits']
            }
        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups

class QuarterDeleteView(LoginRequiredMixin, DeleteView):
    model = Quarter
    context_object_name = "quarter"
    template_name = "section1/quarter_delete.html"
    success_url = reverse_lazy('quarter-list')

    def get_success_url(self):
        return self.success_url
    
class MonthDeleteView(LoginRequiredMixin, DeleteView):
    model = Month
    context_object_name = "month"
    template_name = "section1/month_delete.html"
    
    def get_success_url(self):
        quarter_id = self.object.quarter_id
        return reverse('month-list', kwargs={'quarter_pk': quarter_id})


class FamilyDeleteView(DeleteView):
    model = Family
    context_object_name = "family"
    template_name = "section1/family_delete.html"

    def get_success_url(self):
        month_id = self.object.month_id
        return reverse('family_list', kwargs={'month_id': month_id})

class QuarterDetailView(LoginRequiredMixin, DetailView):
    model = Quarter
    context_object_name = "quarter"
    template_name = "section1/quarter_detail.html"
    
