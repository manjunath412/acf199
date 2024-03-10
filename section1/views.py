import io, csv
from datetime import datetime
from django.db import transaction
from django.db.models import Max, Count, Q
from django.contrib import messages
from django.core.files import File
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
import pandas as pd

from .forms import QuarterForm, MonthForm, FamilyForm, AdultForm, ChildForm, MonthSelectionForm, FileUploadForm, QuarterSelectionForm
from .models import Quarter, Month, Family, Adult, Child, ValidationResult, FileUpload, ImportError, GeneratedFile
from .tasks import DataValidator

class QuarterListView(LoginRequiredMixin, ListView):
    model = Quarter
    context_object_name = "quarters"
    template_name = "section1/quarter_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class MonthListView(LoginRequiredMixin, ListView):
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

class FamilyListView(LoginRequiredMixin, ListView):
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

class AdultListView(LoginRequiredMixin, ListView):
    model = Adult
    context_object_name = 'adults'
    template_name = 'section1/adult_list.html'

    def get_queryset(self):
        return Adult.objects.filter(family_id=self.kwargs['family_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = Family.objects.get(pk=self.kwargs['family_id'])
        context['family'] = family
        context['report_month'] = family.month.report_month
        context['month_id'] = family.month.id
        return context

class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    context_object_name = 'children'
    template_name = 'section1/child_list.html'

    def get_queryset(self):
        return Child.objects.filter(family_id=self.kwargs['family_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = Family.objects.get(pk=self.kwargs['family_id'])
        context['family'] = family
        context['report_month'] = family.month.report_month
        context['month_id'] = family.month.id
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
            
            'TANF Assistance': ['item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'fam_exempt_fed_time_limits',\
                                'item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                                'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
                                'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
                                'item26c3_red_len_assist', 'item26c4_other_non_sanction'],
            'ControlFields': ['month', 'created_by', 'created_at', 'updated_by', 'updated_at']
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
        context['report_month'] = self.month_instance.report_month
        if 'form' in context:
            context['field_groups'] = self.get_field_groups(context['form']) #context['form'].field_groups
        return context
    
    def get_success_url(self):
        return reverse_lazy('family_list', kwargs={'month_id': self.kwargs['month_id']})

class AdultCreateView(LoginRequiredMixin, CreateView):
    model = Adult
    form_class = AdultForm
    template_name = 'section1/adult_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_form_kwargs(self):
        kwargs = super(AdultCreateView, self).get_form_kwargs()
        kwargs['family_id'] = self.kwargs.get('family_id')
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        initial['family'] = self.kwargs.get('family_id')
        return initial
    
    def form_invalid(self, form):
        print("Form is invalid")
        for field in form.errors:
            print("Error in field:", field)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        print("Form is valid")
        try:
            family_instance = get_object_or_404(Family, pk=self.kwargs.get('family_id')) #Family.objects.get(pk=self.kwargs.get('family_id'))
            form.instance.created_by_id = self.request.user.id
            form.instance.updated_by_id = self.request.user.id
        except Month.DoesNotExist:
            form.add_error('case', 'Invalid Case specified!')
        
        form.instance.family = family_instance

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'month_instance'):
            self.family_instance = get_object_or_404(Family, pk=self.kwargs.get('family_id')) #Family.objects.get(pk=self.kwargs['family_id'])
        context['family'] = self.family_instance
        context['report_month'] = self.family_instance.month.report_month
        if 'form' in context:
            context['field_groups'] = self.get_field_groups(context['form']) #context['form'].field_groups
        return context
    
    def get_success_url(self):
        return reverse_lazy('adult_list', kwargs={'family_id': self.kwargs['family_id']})
    
    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Adult Overview': ['family_affiliation', 'noncustodial_parent', 'date_of_birth', 'ssn', \
                'item34a_hispanic_latino', 'item34b_american_indian_alaska_native', 'item34c_asian', \
                'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                'item36a_receives_oasdi', 'item36b_receives_federal_disability', 'item36c_receives_title_xiv_apdt', \
                'item36e_receives_xvi_ssi', 'marital_status', 'relationship_to_hoh','parent_with_minor_child', \
                'educational_level', 'citizenship_immigration_status', 'coop_child_support', 'countable_federal_time_limit_months', \
                'employment_status','work_eligible_individual','work_participation_status', 'family',],

            'Work-Activity Participation ': ['unsubsidized_employment_hours',\
                'subsidized_private_employment_hours', 'subsidized_public_employment_hours', \
                'item53a_wex_participation', 'item53b_wex_excused_absences', 'item53c_wex_holidays', \
                'item55a_jobsearch_participation', 'item55b_jobsearch_excused_absences', 'item55c_jobsearch_holidays', \
                'item56a_commsvs_participation', 'item56b_commsvs_excused_absences', 'item56c_commsvs_holidays',  \
                'item57a_voced_participation', 'item57b_voced_excused_absences', 'item57c_voced_holidays',  \
                'item58a_jst_participation', 'item58b_jst_excused_absences', 'item58c_jst_holidays', \
                'item59a_emped_hsd_participation', 'item59b_emped_hsd_excused_absences', 'item59c_emped_hsd_holidays',  \
                'item60a_schlattnd_participation', 'item60b_schlattnd_excused_absences', 'item60c_schlattnd_holidays',  \
                'item61a_chldcare_participation', 'item61b_chldcare_excused_absences', 'item61c_chldcare_holidays',],

            'Adult-Other': ['deemed_core_hours_overall_rate', 'deemed_core_hours_two_parent_rate', 'earned_income', \
                            'item66b_social_security', 'item66c_ssi', 'item66d_worker_comp', 'item66e_other_unearned_income'],

            'ControlFields': ['created_by', 'created_at', 'updated_by', 'updated_at']
            }

        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups

class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = 'section1/child_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_form_kwargs(self):
        kwargs = super(ChildCreateView, self).get_form_kwargs()
        kwargs['family_id'] = self.kwargs.get('family_id')
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        initial['family'] = self.kwargs.get('family_id')
        return initial
    
    def form_invalid(self, form):
        print("Form is invalid")
        for field in form.errors:
            print("Error in field:", field)
        return super().form_invalid(form)
    
    def form_valid(self, form):
        print("Form is valid")
        try:
            family_instance = Family.objects.get(pk=self.kwargs['family_id'])
            form.instance.family = family_instance
            form.instance.created_by_id = self.request.user.id
            form.instance.updated_by_id = self.request.user.id
        except Family.DoesNotExist:
            form.add_error('case', 'Invalid Case specified!')
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'month_instance'):
            self.family_instance = Family.objects.get(pk=self.kwargs['family_id'])
        context['family'] = self.family_instance
        context['report_month'] = self.family_instance.month.report_month
        if 'form' in context:
            context['field_groups'] = self.get_field_groups(context['form']) #context['form'].field_groups
        return context
    
    def get_success_url(self):
        return reverse_lazy('child_list', kwargs={'family_id': self.kwargs['family_id']})
    
    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Child Overview': ['ssn', 'family_affiliation', 'date_of_birth', 'item34a_hispanic_latino', 'item34b_american_indian_alaska_native', \
                               'item34c_asian', 'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                                'family'],

            'Child-Details': ['disability_non_ssa', 'item72b_ssi_xvi_ssi', 'relation_to_hoh', 'parent_with_minor_child', 'educational_level', \
                            'citizenship_immigration_status', 'item77a_ssa', 'item77b_other_unearned_income'],
            'ControlFields': ['created_by', 'created_at', 'updated_by', 'updated_at']
            }

        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups

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

class FamilyUpdateView(LoginRequiredMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'section1/family_update.html'
    
    def get_success_url(self):
        month_id = self.object.month_id
        return reverse('family_list', kwargs={'month_id': month_id})

    def get_form(self, form_class=None):
        form_class = super().get_form(form_class)
        form_class.field_groups = self.get_field_groups(form_class)
        #form = super().get_form(form_class)
        return form_class

    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Case Overview': ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                            'disposition', 'new_applicant', 'num_family_members', 'family_type', \
                            'receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                            'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            
            'TANF Assistance': ['item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'fam_exempt_fed_time_limits',\
                                'item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                                'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
                                'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
                                'item26c3_red_len_assist', 'item26c4_other_non_sanction'],
            'ControlFields': ['month', 'created_by', 'created_at', 'updated_by', 'updated_at']
            }
        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'month_instance'):
            self.month_instance = Month.objects.get(pk=self.kwargs['month_id'])
        context['month'] = self.month_instance
        context['report_month'] = self.month_instance.report_month
        if 'form' in context:
            context['field_groups'] = self.get_field_groups(context['form']) #context['form'].field_groups
        return context
        
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
    '''
    
class AdultUpdateView(LoginRequiredMixin, UpdateView):
    model = Adult
    form_class = AdultForm
    template_name = 'section1/adult_update.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    
    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Adult Overview': ['family_affiliation', 'noncustodial_parent', 'date_of_birth', 'ssn', \
                'item34a_hispanic_latino', 'item34b_american_indian_alaska_native', 'item34c_asian', \
                'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                'item36a_receives_oasdi', 'item36b_receives_federal_disability', 'item36c_receives_title_xiv_apdt', \
                'item36e_receives_xvi_ssi', 'marital_status', 'relationship_to_hoh','parent_with_minor_child', \
                'educational_level', 'citizenship_immigration_status', 'coop_child_support', 'countable_federal_time_limit_months', \
                'employment_status','work_eligible_individual','work_participation_status'],

            'Work-Activity Participation ': ['unsubsidized_employment_hours',\
                'subsidized_private_employment_hours', 'subsidized_public_employment_hours', \
                'item53a_wex_participation', 'item53b_wex_excused_absences', 'item53c_wex_holidays', \
                'item55a_jobsearch_participation', 'item55b_jobsearch_excused_absences', 'item55c_jobsearch_holidays', \
                'item56a_commsvs_participation', 'item56b_commsvs_excused_absences', 'item56c_commsvs_holidays',  \
                'item57a_voced_participation', 'item57b_voced_excused_absences', 'item57c_voced_holidays',  \
                'item58a_jst_participation', 'item58b_jst_excused_absences', 'item58c_jst_holidays', \
                'item59a_emped_hsd_participation', 'item59b_emped_hsd_excused_absences', 'item59c_emped_hsd_holidays',  \
                'item60a_schlattnd_participation', 'item60b_schlattnd_excused_absences', 'item60c_schlattnd_holidays',  \
                'item61a_chldcare_participation', 'item61b_chldcare_excused_absences', 'item61c_chldcare_holidays',],

            'Adult-Other': ['deemed_core_hours_overall_rate', 'deemed_core_hours_two_parent_rate', 'earned_income', \
                            'item66b_social_security', 'item66c_ssi', 'item66d_worker_comp', 'item66e_other_unearned_income'],

            'ControlFields': ['family', 'created_by', 'created_at', 'updated_by', 'updated_at']
            }

        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        # Add family case number directly to the context for display purposes
        context['family_case_number'] = self.object.family.case_number
        context['report_month'] = self.object.family.month.report_month
        return context
    
    def get_success_url(self):
        family_id = self.object.family.id
        return reverse_lazy('adult_list', kwargs={'family_id': family_id})

class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = 'section1/child_update.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_field_groups(self, form):
        FIELD_GROUPS = {
            'Child Overview': ['ssn', 'family_affiliation', 'date_of_birth', 'item34a_hispanic_latino', 'item34b_american_indian_alaska_native', \
                               'item34c_asian', 'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                                ],
            'Child-Details': ['disability_non_ssa', 'item72b_ssi_xvi_ssi', 'relation_to_hoh', 'parent_with_minor_child', 'educational_level', \
                            'citizenship_immigration_status', 'item77a_ssa', 'item77b_other_unearned_income'],
            'ControlFields': ['family', 'created_by', 'created_at', 'updated_by', 'updated_at']
            }

        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [form[field] for field in field_names if field in form.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups
    
    def get_success_url(self):
        family_id = self.object.family.id
        return reverse_lazy('child_list', kwargs={'family_id': family_id})

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

class AdultDeleteView(LoginRequiredMixin, DeleteView):
    model = Adult
    context_object_name = "adult"
    template_name = "section1/adult_delete.html"

    def get_success_url(self):
        family_id = self.kwargs['family_id']
        return reverse('adult_list', kwargs={'family_id': family_id})

class ChildDeleteView(LoginRequiredMixin, DeleteView):
    model = Child
    context_object_name = "child"
    template_name = "section1/child_delete.html"

    def get_success_url(self):
        family_id = self.kwargs['family_id']
        return reverse('child_list', kwargs={'family_id': family_id})

class QuarterDetailView(LoginRequiredMixin, DetailView):
    model = Quarter
    context_object_name = "quarter"
    template_name = "section1/quarter_detail.html"

class ValidationBaseView(LoginRequiredMixin, TemplateView):
    template_name = 'section1/validation_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MonthSelectionForm(self.request.POST or None)
        context['validated_months'] = ValidationResult.objects.values_list('report_month', flat=True).distinct()
        return context

class ValidateDataView(TemplateView):
    template_name = 'section1/validate_data.html'
    #validation_errors = []
    # Generate the list of valid FIPS codes
    def generate_valid_fips_codes():
        # Define the ranges and specific values as provided
        ranges = [(1, 2), (4, 6), (8, 13), (15, 42), (44, 51), (53, 56)]
        specific_values = [60, 66, 72, 78]

        # Generate all values within the ranges
        valid_codes = []
        for start, end in ranges:
            valid_codes.extend([str(n).zfill(2) for n in range(start, end + 1)])
        
        # Add specific values, ensuring they are formatted as two-digit strings
        valid_codes.extend([str(n).zfill(2) for n in specific_values])

        return valid_codes
    
    valid_fips_codes = generate_valid_fips_codes()
    def get_month_stats(self):
        month_stats = []
        latest_versions = ValidationResult.objects.values('report_month').annotate(
                            latest_version=Max('version'),
                            max_updated_at=Max('updated_at')
                            )
        if latest_versions is not None:
            for month_version in latest_versions:
                report_month = month_version['report_month']
                version = month_version['latest_version']
                latest_run_date = month_version['max_updated_at']
                
                errors_count = ValidationResult.objects.filter(
                    report_month=report_month, 
                    version=version,
                    edit_type='FATAL'
                ).count()
                
                no_errors_count = ValidationResult.objects.filter(
                    report_month=report_month, 
                    version=version,
                    edit_type='NOERROR'
                ).count()
                
                month_stats.append({
                    'month': report_month,
                    'errors_count': errors_count,
                    'no_errors_count': no_errors_count,
                    'version': version,
                    'max_updated_at': latest_run_date
                })
            return month_stats
                            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month_stats = self.get_month_stats()
        context['form'] = MonthSelectionForm()
        #context['validated_months'] = ValidationResults.objects.values_list('report_month', flat=True).distinct()
        context['month_stats'] = month_stats
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        form = MonthSelectionForm(request.POST)
        if form.is_valid():
            report_month = form.cleaned_data['report_month'].report_month
            #version = self.perform_validation(request.user, report_month)
            self.init_validation(request.user, report_month)
            #if version is not None:
                # Fetch validation results for the current report_month and version
            #    validation_results = ValidationResults.objects.filter(report_month=report_month, version=version)
            #    context = {'form': form, 'validation_results': validation_results}
            #else:
            #    context = {'form': form, 'message': 'Validation completed, but no results were found.'}
            #messages.success(request, 'Validation completed successfully.')
            return redirect('validate_data')
            #return render(request, self.template_name, context)
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
        
        return self.render_to_response(self.get_context_data(form=form))
        #return render(request, self.template_name, {'form': form})
    
    def get_next_version(self, report_month):
        latest_validation = ValidationResult.objects.filter(report_month=report_month).order_by('-version').first()
        return (latest_validation.version + 1) if latest_validation else 1

    def init_validation(self, user, report_month):
        print(report_month)
        try:
            month_instance = Month.objects.get(report_month=report_month)
        except Month.DoesNotExist:
            print("Selected month does not exist.")
            return
        
        version = self.get_next_version(report_month)
        validator = DataValidator(user, version, report_month)
        validator.perform_validation()

class ErrorListView(LoginRequiredMixin, ListView):
    model = ValidationResult
    context_object_name = 'errors'
    template_name = 'section1/error_list.html'

    def get_queryset(self):
        sort = self.request.GET.get('sort', None)
        if sort == 'edit_number':
            order_by = ('edit_number',)
        elif sort == 'item_number':
            order_by = ('item_number',)
        else:
            order_by = ('edit_type', 'item_number')
        
        return ValidationResult.objects.filter(report_month=self.kwargs['month'], 
                                                version = self.kwargs['version']).order_by(*order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        errors = self.get_queryset()
        paginator = Paginator(errors, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        month = self.kwargs['month']
        version = self.kwargs['version']

        max_updated_at = self.model.objects.filter(
            report_month=month, 
            version=version
        ).aggregate(max_updated_at=Max('updated_at'))['max_updated_at']

        context['month'] = month
        context['version'] = version
        context['last_validated_on'] = max_updated_at
        context['page_obj'] = page_obj
        return context
    
class FileUploadView(LoginRequiredMixin, FormView):
    template_name = 'section1/file_upload.html'
    form_class = FileUploadForm
    
    def get_success_url(self):
        month_id = self.kwargs.get('month_id')
        if month_id:
            return reverse('file_upload', kwargs={'month_id': month_id})
        
    def get_initial(self):
        initial = super().get_initial()
        month_id = self.kwargs.get('month_id')
        if month_id:
            month = get_object_or_404(Month, pk=month_id)
            initial['month'] = month
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month_id = self.kwargs.get('month_id')
        if month_id:
            month = get_object_or_404(Month, pk=month_id)
            context['month'] = month.report_month
            prior_uploads = FileUpload.objects.filter(month=month).order_by('-uploaded_at')
            context['prior_uploads'] = prior_uploads
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    def form_valid(self, form):
        month = Month.objects.get(report_month=form.cleaned_data['month'])
        model_type = form.cleaned_data['model_type']
        uploaded_file = self.request.FILES.get('file')
        if not (uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx')):
            form.add_error('file', "Unsupported file type. Please upload a .csv or .xls(x) file.")
            return self.form_invalid(form)
        
        file_upload_instance = FileUpload(
            month=month,
            model_type=form.cleaned_data['model_type'],
            uploaded_by=self.request.user,
            file=uploaded_file
        )
        upload_instance = FileUpload.objects.last()
        
        file_content = uploaded_file.read().decode('utf-8')
        file_like = io.StringIO(file_content)
        
        is_valid = validate_csv_headers(file_like, FamilyForm)
        if not is_valid:
            form.add_error(None, "File headers do not match expected fields.")
            return self.form_invalid(form)
        else:
            file_like = io.StringIO(file_content)
            process_file(file_like, FamilyForm, ImportError, model_type, month, upload_instance, self.request.user)
        file_upload_instance.save()

        model_verbose = dict(form.fields['model_type'].choices).get(model_type)
        messages.success(self.request, f'{model_verbose} Datafile successfully uploaded.')
        return super().form_valid(form)

def validate_csv_headers(file_like, form_class):
    expected_headers = [field for field in form_class.Meta.fields]

    reader = csv.DictReader(file_like)
    if set(header.strip() for header in reader.fieldnames) != set(expected_headers):
        return False
    return True

def process_file(file, form_class, error_model, model_type, month, upload_instance, user):
    reader = csv.DictReader(file)
    valid_rows = []
    with transaction.atomic():
        for row in reader:
            form = form_class(data=row)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.month = month
                instance.created_by = user
                instance.updated_by = user
                instance.save()
                valid_rows.append(form.cleaned_data)
                form.save()
            else:
                error_model.objects.create(
                    upload=upload_instance,
                    model_type=model_type,
                    original_data=row,
                    errors=form.errors.as_json(),
                    created_by=user,
                    updated_by=user
                )

class ProcessQuarterView(LoginRequiredMixin, FormView):
    template_name = 'section1/process_quarter.html'
    form_class = QuarterSelectionForm
    success_url = reverse_lazy('create_file') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context = super(ProcessQuarterView, self).get_context_data(**kwargs)
        context['files'] = GeneratedFile.objects.all().order_by('-created_at') 
        return context
    
    def form_valid(self, form):
        report_quarter = form.cleaned_data['report_quarter']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"{report_quarter}_{timestamp}.txt"
        user = self.request.user
        result = process_quarter(report_quarter.id, output_file_name,user)
        if result:
            messages.success(self.request, "Quarter processed successfully.")
            return redirect('create_file')
        else:
            messages.success(self.request, "Quarter did not process successfully.")
        return super().form_valid(form)
        #return redirect('create_file')
        #return super(ProcessQuarterView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('create_file')

def concatenate_model_fields(instance):
    field_values = []
    exclude_fields = ['family', 'id', 'month', 'created_at', 'updated_at', 'created_by', 'updated_by']
    for field in instance._meta.get_fields():
        if field.concrete and not field.is_relation and field.name not in exclude_fields:
            field_value = getattr(instance, field.name, '')
            field_values.append(str(field_value))
    return "".join(field_values)

def process_quarter(quarter_id, output_file_name, user):
    record_count = 0 
    output_file_path = f'{output_file_name}'
    try:
        quarter = Quarter.objects.get(id=quarter_id)
    except Quarter.DoesNotExist:
        print("Quarter not found")
        return

    with open(output_file_path, 'w') as file:
        file.write("Header: Processing records for Quarter ID {}\n".format(quarter_id))
        for month in quarter.month_set.all():
            for family in month.family_set.all():
                family_data = "T1" + family.month.report_month + concatenate_model_fields(family)
                file.write(family_data + "\n")
                record_count += 1
                for adult in family.adult_set.all():
                    adult_data = "T2" + family.month.report_month + family.case_number + concatenate_model_fields(adult)
                    file.write(adult_data + "\n")
                    record_count += 1

                children = list(family.child_set.all())
                for i in range(0, len(children), 2):
                    child_data = "T3" + family.month.report_month + family.case_number
                    child_data += concatenate_model_fields(children[i])
                    if i + 1 < len(children):
                        child_data += concatenate_model_fields(children[i + 1])
                    file.write(child_data + "\n")
                    record_count += 1
        file.write("Trailer: Total Records Processed {}\n".format(record_count))

    with open(output_file_path, 'rb') as file_for_upload:        
        django_file = File(file_for_upload)
        generated_file = GeneratedFile(quarter=quarter, name=output_file_name, file=django_file, created_by=user)
        generated_file.save()

    #print(f"File {output_file_name} saved with ID {generated_file.name}")
    return True
'''
class ListFilesView(LoginRequiredMixin, FormView):
    template_name = 'section1/list_files.html'
    form_class = QuarterSelectionForm
    success_url = reverse_lazy('list_files')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter = self.request.GET.get('quarter')

        if quarter:
            print('e')
            files = GeneratedFile.objects.filter(quarter_id=quarter)
            context['files'] = files
            print(context)

        return context

    def form_valid(self, form):
        quarter = form.cleaned_data['quarter']
        files = GeneratedFile.objects.filter(quarter=quarter)
        return self.render_to_response(self.get_context_data(files=files))
'''