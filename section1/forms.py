from django import forms
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Div, Row, Column
from .models import Quarter, Month, Family, Adult, Child, FileUpload

class QuarterForm(forms.ModelForm):
    class Meta:
        model = Quarter
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(QuarterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = self.get_form_layout()

    def get_form_layout(self):
        form_layout = Layout()
        for field_name, _ in self.fields.items():
            form_layout.append(Field(field_name, css_class='form-control'))
        form_layout.append(ButtonHolder(
            Submit('submit', 'Save', css_class='btn btn-primary')
        ))
        return form_layout

class MonthForm(forms.ModelForm):
    class Meta:
        model = Month
        fields = ['quarter', 'report_month', 'start_date', 'end_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_quarter = kwargs.get('initial', {}).get('quarter')
        if initial_quarter:
            self.fields['quarter'].initial = initial_quarter
        self.fields['quarter'].widget = forms.HiddenInput()
        
class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                'disposition', 'new_applicant', 'num_family_members', 'family_type', \
                'receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources',\
                'item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months', 'item26a1_sanc_redux_amt', \
                'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction',\
                'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap',\
                'item26c3_red_len_assist', 'item26c4_other_non_sanction', 'fam_exempt_fed_time_limits']
        
        def clean(self):
            cleaned_data = super().clean()
            for field_name, field_value in cleaned_data.items():
                if field_value and isinstance(self.fields[field_name], forms.CharField):
                    if self._is_valid_integer(field_value):
                        max_length = self.fields[field_name].max_length
                        cleaned_data[field_name] = field_value.zfill(max_length)
                    else:
                        self.add_error(field_name, f"Value must be an integer and fit within its length of {max_length}.")
        
    '''
    def get_field_groups(self):
        FIELD_GROUPS = {
            'Case Overview': ['case_number', 'county_fips_code', 'stratum', 'zip_code', 'funding_stream', \
                            'disposition', 'new_applicant', 'num_family_members', 'family_type'],
            'Benefits': ['receives_subsidized_housing', 'receives_medical_assistance', 'snap_amount', \
                        'subsid_child_care_amount', 'child_support_amount', 'family_cash_resources' ],
            'TANF Assistance': ['item21a_amount', 'item21b_nbr_month', 'item22a_amount', 'item22b_children_covered', \
                                'item22c_nbr_months', 'item23a_amount', 'item23b_nbr_months'],
            'TANF Assistance Redux': ['item26a1_sanc_redux_amt', 'item26a2_work_req_sanction', 'item26a4_teen_prnt_schl_attend_sanc', \
                                    'item26a5_child_support_non_coop', 'item26a6_irp_non_coop', 'item26a7_other_sanction', \
                                        'item26b_recoupment', 'item26c1_other_tot_red_amount', 'item26c2_family_cap', \
                                            'item26c3_red_len_assist', 'item26c4_other_non_sanction' ],
            'TANF Federal Time Limit Exemption': ['fam_exempt_fed_time_limits']
            }
        groups = []
        for title, field_names in FIELD_GROUPS.items():
            fields = [self[field] for field in field_names if field in self.fields]
            if fields:
                groups.append({'title': title, 'fields': fields})
        return groups
    '''
class AdultForm(forms.ModelForm):
    class Meta:
        model = Adult
        #fields = '__all__'
        fields = ['family','family_affiliation', 'noncustodial_parent', 'date_of_birth', 'ssn', \
                'item34a_hispanic_latino', 'item34b_american_indian_alaska_native', 'item34c_asian', \
                'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                'item36a_receives_oasdi', 'item36b_receives_federal_disability', 'item36c_receives_title_xiv_apdt', \
                'item36e_receives_xvi_ssi', 'marital_status', 'relationship_to_hoh','parent_with_minor_child', \
                'educational_level', 'citizenship_immigration_status', 'coop_child_support', 'countable_federal_time_limit_months', \
                'employment_status','work_eligible_individual','work_participation_status','unsubsidized_employment_hours',\
                'subsidized_private_employment_hours', 'subsidized_public_employment_hours', \
                'item53a_wex_participation', 'item53b_wex_excused_absences', 'item53c_wex_holidays', \
                'item55a_jobsearch_participation', 'item55b_jobsearch_excused_absences', 'item55c_jobsearch_holidays', \
                'item56a_commsvs_participation', 'item56b_commsvs_excused_absences', 'item56c_commsvs_holidays',  \
                'item57a_voced_participation', 'item57b_voced_excused_absences', 'item57c_voced_holidays',  \
                'item58a_jst_participation', 'item58b_jst_excused_absences', 'item58c_jst_holidays', \
                'item59a_emped_hsd_participation', 'item59b_emped_hsd_excused_absences', 'item59c_emped_hsd_holidays',  \
                'item60a_schlattnd_participation', 'item60b_schlattnd_excused_absences', 'item60c_schlattnd_holidays',  \
                'item61a_chldcare_participation', 'item61b_chldcare_excused_absences', 'item61c_chldcare_holidays',  \
                'deemed_core_hours_overall_rate', 'deemed_core_hours_two_parent_rate', 'earned_income', \
                'item66b_social_security', 'item66c_ssi', 'item66d_worker_comp', 'item66e_other_unearned_income'
                ]
    
    def __init__(self, *args, **kwargs):
        family_id = kwargs.pop('family_id', None)
        super(AdultForm, self).__init__(*args, **kwargs)
        if family_id:
            self.fields['family'].initial = family_id
            self.fields['family'].widget = forms.HiddenInput()
        
        if self.instance.pk and self.instance.family:
            self.fields['family'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        for field_name, field_value in cleaned_data.items():
            if field_value and isinstance(self.fields[field_name], forms.CharField):
                if self._is_valid_integer(field_value):
                    max_length = self.fields[field_name].max_length
                    cleaned_data[field_name] = field_value.zfill(max_length)
                else:
                    self.add_error(field_name, f"Value must be an integer and fit within its length of {max_length}.")

        total_participation_value = int(cleaned_data['item59a_emped_hsd_participation']) + int(cleaned_data['item60a_schlattnd_participation']) + int(cleaned_data['item61a_chldcare_participation'])
        cleaned_data['item59a_emped_hsd_participation'] = f"{total_participation_value:02d}"

        total_excused_absences = int(cleaned_data['item59b_emped_hsd_excused_absences']) + int(cleaned_data['item60b_schlattnd_excused_absences']) + int(cleaned_data['item61b_chldcare_excused_absences'])
        cleaned_data['item59b_emped_hsd_excused_absences'] = f"{total_excused_absences:02d}"

        total_holidays = int(cleaned_data['item59c_emped_hsd_holidays']) + int(cleaned_data['item60c_schlattnd_holidays']) + int(cleaned_data['item61c_chldcare_holidays'])
        cleaned_data['item59c_emped_hsd_holidays'] = f"{total_holidays:02d}"
    
        dob = cleaned_data.get('date_of_birth')
        if dob and not self._is_valid_dob_format(dob):
            self.add_error('date_of_birth', "DOB must be in YYYYMMDD format and a valid date.")

        return cleaned_data

    def _is_valid_integer(self, value):
        try:
            int_value = int(value)
            return True
        except ValueError:
            return False
        
    def _is_valid_dob_format(self, dob):
        try:
            datetime.strptime(dob, '%Y%m%d')
            return True
        except ValueError:
            return False
        
class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['family', 'ssn', 'family_affiliation', 'date_of_birth', 'item34a_hispanic_latino', 'item34b_american_indian_alaska_native',\
                 'item34c_asian', 'item34d_black', 'item34e_native_pacific_islander', 'item34f_white', 'gender', \
                'disability_non_ssa', 'item72b_ssi_xvi_ssi', 'relation_to_hoh', 'parent_with_minor_child', 'educational_level', \
                'citizenship_immigration_status', 'item77a_ssa', 'item77b_other_unearned_income'
                ]    
    
    def __init__(self, *args, **kwargs):
        family_id = kwargs.pop('family_id', None)
        super(ChildForm, self).__init__(*args, **kwargs)
        if family_id:
            self.fields['family'].initial = family_id
            self.fields['family'].widget = forms.HiddenInput()
        
        if self.instance.pk and self.instance.family:
            self.fields['family'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        for field_name, field_value in cleaned_data.items():
            if field_value and isinstance(self.fields[field_name], forms.CharField):
                if self._is_valid_integer(field_value):
                    max_length = self.fields[field_name].max_length
                    cleaned_data[field_name] = field_value.zfill(max_length)
                else:
                    self.add_error(field_name, f"Value must be an integer and fit within its length of {max_length}.")

        dob = cleaned_data.get('date_of_birth')
        if dob and not self._is_valid_dob_format(dob):
            self.add_error('date_of_birth', "DOB must be in YYYYMMDD format and a valid date.")

        return cleaned_data

    def _is_valid_integer(self, value):
        try:
            int_value = int(value)
            return True
        except ValueError:
            return False
        
    def _is_valid_dob_format(self, dob):
        try:
            datetime.strptime(dob, '%Y%m%d')
            return True
        except ValueError:
            return False

class MonthSelectionForm(forms.Form):
    report_month = forms.ModelChoiceField(queryset=Month.objects.all().order_by('-report_month'), to_field_name="report_month", empty_label="Select a month")

class FileUploadForm(forms.Form):
    model = FileUpload
    fields = ['month', 'model_type', 'file'] 

    MODEL_CHOICES = [
        ('family', 'Family'),
        ('adult', 'Adult'),
        ('child', 'Child'),
    ]
    model_type = forms.ChoiceField(choices=MODEL_CHOICES, required=True)
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        initial = kwargs.get('initial', {})
        month_initial = initial.get('month', None)
        super(FileUploadForm, self).__init__(*args, **kwargs)

        if month_initial:
            self.fields['month'] = forms.CharField(widget=forms.HiddenInput(), initial=month_initial)
        else:
            MONTH_CHOICES = [(month.id, str(month)) for month in Month.objects.all()]
            self.fields['month'] = forms.ChoiceField(choices=MONTH_CHOICES)

        self.order_fields(['month', 'model_type', 'file'])

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            if not (str(file.name).endswith('.csv') or str(file.name).endswith('.xls') or str(file.name).endswith('.xlsx')):
                raise ValidationError("Unsupported file type. Please upload a .csv or .xls(x) file.")
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size must be under 5MB")
        return file

class QuarterSelectionForm(forms.Form):
    #class Meta:
    #    model = Quarter
        #fields = ['report_quarter']
        #QUARTER_CHOICES = [(quarter.id, str(quarter)) for quarter in Quarter.objects.all()]
        #report_quarter = forms.ChoiceField(choices=QUARTER_CHOICES, required=True)
    report_quarter = forms.ModelChoiceField(queryset=Quarter.objects.all().order_by('-id'), to_field_name="report_quarter", empty_label="Select a Quarter")