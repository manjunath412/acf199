from .models import Family, Adult, Child, ValidationResult
from django.db.models import Q

class DataValidator:
    def __init__(self, user, version, report_month=None):
        self.user = user
        self.report_month=report_month
        self.version=version
        print(self.version)
    
    def create_validation_error(self, edit_number, item_number, description, edit_values, edit_type, family=None, adult=None):
        ValidationResult.objects.create(
                report_month=self.report_month,
                version=self.version,
                edit_type = edit_type,
                edit_number = edit_number,
                item_number = item_number,
                description = description,
                edit_values=edit_values,
                created_by=self.user,
                updated_by=self.user,
                family=family,
                adult=adult,
            )
    
    def get_next_version(self):
        latest_validation = ValidationResult.objects.filter(report_month=self.report_month).order_by('-version').first()
        return (latest_validation.version + 1) if latest_validation else 1

    def perform_validation(self):
        self.validate_case_numbers()
        self.validate_dispositions()
        self.validate_dispositions()
        self.validate_number_family_members()
        self.validate_family_type()
        self.validate_family_affiliation()
        self.validate_adult_dob()
        self.validate_adult_ssn()
        self.validate_race_ethnicity()
        self.validate_marital_status()
        self.validate_relationship_to_hoh()
        self.validate_parent_with_minor()
        self.validate_education_level()
        self.validate_citizenship_immigration_status()
        self.validate_coop_child_support()
        self.validate_countable_federal_time_limit_months()
        self.validate_employment_status()
        self.validate_work_participation_status()
        self.validate_work_activity_hours()
        self.closeout_validation()        
        self.validate_child_family_affiliation        
        self.validate_child_race_ethnicity()        
        self.validate_child_relationship_to_hoh()        
        self.validate_education_level()
        self.validate_citizenship_immigration_status()

    def closeout_validation(self):
        closeout_version = ValidationResult.objects.filter(report_month=self.report_month).order_by('-version').first()
        if closeout_version is not None:
            if closeout_version.version != self.version:
                #self.version += 1
                self.create_validation_error('T-000', '000', 'NO ERRORS','NO ERRORS', 'NO ERRORS')

    def validate_case_numbers(self):
        missing_cases = Family.objects.filter(case_number__isnull=True, case_number='')
        for family in missing_cases:
            self.self.create_validation_error('T1-004', '6', 'CASE NUMBER', 'ITEM 6? MUST NOT BE BLANK', 'FATAL', family=family) 

    def validate_dispositions(self):
        #ITEM 9 MUST = 1-2 
        #IF ITEM 9 = 2, THEN ITEMS 1,4-6 MUST NOT BE BLANK 
        invalid_dispositions = Family.objects.exclude(disposition__in=[1,2])
        for family in invalid_dispositions:
            self.create_validation_error('T1-008', '9', 'DISPOSITION', 'ITEM 9 MUST = 1-2', 'FATAL', family=family)

    def validate_number_family_members(self):
        invalid_numbers = Family.objects.filter(num_family_members=0)
        for family in invalid_numbers:
            self.create_validation_error('T1-010', '11', 'NUMBER OF FAMILY MEMBERS', 'ITEM 11 MUST > 0', 'FATAL', family=family)

    def validate_family_type(self):
        exclude_types = [1,2,3]
        invalid_family_types = Family.objects.exclude(family_type__in=exclude_types)
        for family in invalid_family_types:
            self.create_validation_error('T1-011', '12', 'FAMILY TYPE FOR WORK PARTICIPATION', 'ITEM 12 MUST = 1-3', 'FATAL', family=family)

    def validate_family_affiliation(self):
        exclude_list = [1,2,3,4,5]
        invalid_affiliations = Adult.objects.exclude(family_affiliation__in=exclude_list)
        for adult in invalid_affiliations:
            self.create_validation_error('T1-014', '30', 'FAMILY AFFILIATION -ADULT', 'ITEM 30 MUST = 1-5 ', 'FATAL', family=adult.family, adult=adult)

    def validate_adult_dob(self):
        #IF ITEM 32 = 99999999 ITEM 30 MUST = 2-5
        #IF ITEM 32 MUST NOT BE BLANK OR ZEROES
        exclude_list = [2,3,4,5]
        adults = Adult.objects.filter(date_of_birth = '', date_of_birth__isnull=True)
        for adult in adults:
            self.create_validation_error('T1-015', '32', 'DATE OF BIRTH -ADULT', 'ITEM 32 MUST NOT BE BLANK OR ZEROES', 'FATAL', family=adult.family, adult=adult)

        adults = Adult.objects.filter(date_of_birth='99999999').exclude(family_affiliation__in=exclude_list)
        for adult in adults:
            self.create_validation_error('T1-016', '32', 'DATE OF BIRTH -ADULT', 'IF ITEM 32 = 99999999 ITEM 30 MUST = 2-5', 'FATAL',family=adult.family, adult=adult)

    def validate_adult_ssn(self):
        invalid_ssns = Adult.objects.filter(Q(ssn='') | Q(ssn__isnull=True))
        invalid_ssn_affiliations= Adult.objects.filter(ssn='999999999', family_affiliation=1)
        for invalid_ssn in invalid_ssns:
            self.create_validation_error('T1-017', '33', 'SSN -ADULT', 'ITEM 33 MUST NOT BE BLANK', 'FATAL', family=invalid_ssn.family, adult=invalid_ssn)

        for invalid_ssn_affiliation in invalid_ssn_affiliations:
            self.create_validation_error('T1-018', '33', 'SSN -ADULT', 'IF ITEM 33 = 999999999 ITEM 30 MUST = 2-5', 'FATAL', family=invalid_ssn_affiliation.family, adult=invalid_ssn_affiliation) 

    def validate_race_ethnicity(self):
        #IF ITEM 34A = BLANK ITEM 30 MUST = 5
        #IF ITEM 30= 1-4, ITEM 34A MUST = 1 OR 2
        exclude_list = [1,2]
        exclude_affiliation_list = [1,2,3,4]
        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34a_hispanic_latino__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34a_hispanic_latino='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-019', '34', 'RACE/ETHNICITY', \
                        'IF ITEM 34A = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-020', '34', 'RACE/ETHNICITY', \
                                    'IF ITEM 30= 1-4, ITEM 34A MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34b_american_indian_alaska_native__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34b_american_indian_alaska_native='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-021', '34', 'RACE/ETHNICITY', 'IF ITEM 34B = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:
                        self.create_validation_error('T1-022', '34', 'RACE/ETHNICITY', 'IF ITEM 30= 1-4, ITEM 34B MUST = 1 OR 2', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)
    
        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34c_asian__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34c_asian='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-023', '34', 'RACE/ETHNICITY','IF ITEM 34C = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-024', '34', 'RACE/ETHNICITY', 'IF ITEM 30= 1-4, ITEM 34C MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34d_black__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34d_black='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
                        self.create_validation_error('T1-024', '34', 'RACE/ETHNICITY','IF ITEM 34D = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:        
            self.create_validation_error('T1-025', '34', 'RACE/ETHNICITY','IF ITEM 34D = BLANK ITEM 30 MUST = 5', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34e_native_pacific_islander__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34e_native_pacific_islander='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:        
            self.create_validation_error('T1-025', '34', 'RACE/ETHNICITY', 'IF ITEM 34E = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-026', '34', 'RACE/ETHNICITY', 'IF ITEM 30= 1-4, ITEM 34E MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34f_white__in = exclude_list)
        blank_race_affilitations = Adult.objects.filter(item34f_white='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:        
            self.create_validation_error('T1-027', '34', 'RACE/ETHNICITY', 'IF ITEM 34F = BLANK ITEM 30 MUST = 5', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)            

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-028', '34', 'RACE/ETHNICITY', 'IF ITEM 30= 1-4, ITEM 34F MUST = 1 OR 2', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

    def validate_marital_status(self):
        #IF ITEM 37 = BLANK, ITEM 30 MUST = 5
        #IF ITEM 30 = 1-4, ITEM 37 MUST = 1-5
        exclude_list = [1,2,3,4,5]
        exclude_affiliation_list = [1,2,3,4]
        invalid_37_affiliations = Adult.objects.filter(marital_status='', family_affiliation__in=exclude_affiliation_list)
        invalid_37s = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(marital_status__in=exclude_list)
        for invalid_37_affiliation in invalid_37_affiliations:
            self.create_validation_error('T1-031', '37', 'MARITAL STATUS','IF ITEM 37 = BLANK, ITEM 30 MUST = 5', 'FATAL', family=invalid_37_affiliation.family,adult=invalid_37_affiliation)

        for invalid_37 in invalid_37s:
            self.create_validation_error('T1-032', '37', 'MARITAL STATUS', 'IF ITEM 30 = 1-4, ITEM 37 MUST = 1-5', 'FATAL', family=invalid_37.family, adult=invalid_37)

    def validate_relationship_to_hoh(self):
        exclude_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
        invalid_hoh_relations = Adult.objects.exclude(relationship_to_hoh__in=exclude_list)

        for invalid_hoh_relation in invalid_hoh_relations:
            self.create_validation_error('T1-033', '38', 'RELATIONSHIP TO HEAD OF HOUSEHOLD', 'ITEM 38 MUST = 01-10', 'FATAL', family=invalid_hoh_relation.family, adult=invalid_hoh_relation) 

    def validate_parent_with_minor(self):
        #IF ITEM 30 = 1,2,4 , ITEM 39 MUST = 1-3
        #IF ITEM 39 = BLANK, ITEM 30 MUST = 3 OR 5
        exclude_list = [1,2,3]
        exclude_affiliation_list1 = [1,2,4]
        exclude_affiliation_list2 = [3,5]
        invalid_39_affiliations = Adult.objects.filter(parent_with_minor_child='', parent_with_minor_child__isnull=True, ).exclude(family_affiliation__in=exclude_affiliation_list2)
        invalid_39s = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list1).exclude(parent_with_minor_child__in=exclude_list)
        for invalid_39_affiliation in invalid_39_affiliations:
            self.create_validation_error('T1-034', '39', 'PARENT WITH MINOR CHILD IN THE FAMILY','IF ITEM 39 = BLANK, ITEM 30 MUST = 3 OR 5', 'FATAL', family=invalid_39_affiliation.family, adult=invalid_39_affiliation)
            
        for invalid_39 in invalid_39s:
            self.create_validation_error('T1-035', '39', 'PARENT WITH MINOR CHILD IN THE FAMILY', 'IF ITEM 30 = 1,2,4 , ITEM 39 MUST = 1-3', 'FATAL', family=invalid_39.family, adult=invalid_39)

    def validate_education_level(self):
        #IF ITEM 30 = 2-5 ITEM 41 MUST =? 01-16,98,99
        #IF ITEM 30 = 1, ITEM 41 MUST = 01-16,98
        #IF ITEM 41 = BLANK, ITEM 30 MUST = 5
        exclude_list1 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '98', '99']
        exclude_list2 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '98', '99']
        exclude_affiliation_list1 = [2,3,4,5]
        exclude_affiliation_list2 = [1]
        exclude_affiliation_list3 = [1,2,3,4]
        excluded_affiliation_adult_list = Adult.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_41_affiliations = excluded_affiliation_adult_list.exclude(educational_level__in=exclude_list1)
        invalid_41s = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list2).exclude(educational_level__in=exclude_list2)
        invalid_41bs = Adult.objects.filter(educational_level=5).exclude(family_affiliation__in=exclude_affiliation_list3)
        for invalid_41_affiliation in invalid_41_affiliations:
            self.create_validation_error('T1-036', '41', 'EDUCATION LEVEL','IF ITEM 30 = 2-5 ITEM 41 MUST =? 01-16,98,99', 'FATAL', family=invalid_41_affiliation.family,adult=invalid_41_affiliation)
            
        for invalid_41 in invalid_41s:
            self.create_validation_error('T1-037', '41', 'EDUCATION LEVEL', 'IF ITEM 30 = 1, ITEM 41 MUST = 01-16,98', 'FATAL',family=invalid_41.family,adult=invalid_41)

        for invalid_41b in invalid_41bs:
            self.create_validation_error('T1-038', '41', 'EDUCATION LEVEL', 'IF ITEM 41 = BLANK, ITEM 30 MUST = 5', 'FATAL', family=invalid_41b.family, adult=invalid_41b)

    def validate_citizenship_immigration_status(self):
        #IF ITEM 42 = BLANK, ITEM 30 MUST = 5
        #IF ITEM 30 = 1-4, ITEM 42 MUST = 1-2,9,
        exclude_list = [1,2,9]
        exclude_affiliation_list1 = [1,2,3,4]
        exclude_affiliation_list2 = [5]
        excluded_affiliation_adult_list = Adult.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_39_affiliations = excluded_affiliation_adult_list.exclude(citizenship_immigration_status__in=exclude_list)
        invalid_39s = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list2).exclude(citizenship_immigration_status='')
        for invalid_39_affiliation in invalid_39_affiliations:
            self.create_validation_error('T1-040', '42', 'CITIZENSHIP/ALIENAGE','IF ITEM 42 = BLANK, ITEM 30 MUST = 5', 'FATAL', family=invalid_39_affiliation.family,adult=invalid_39_affiliation)
        
        for invalid_39 in invalid_39s:
            self.create_validation_error('T1-041', '42', 'CITIZENSHIP/ALIENAGE', 'IF ITEM 30 = 1-4, ITEM 42 MUST = 1-2,9', 'FATAL', family=invalid_39.family,adult=invalid_39)
    
    def validate_coop_child_support(self):
        #ITEM 43 MUST = 1-2, OR 9
        #IF ITEM 43 = BLANK, ITEM 30 MUST = 5
        exclude_list = [1,2,9]
        exclude_affiliation_list1 = [1,2,3,4]
        exclude_affiliation_list2 = [5]
        excluded_affiliation_adult_list = Adult.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_41_affiliations = excluded_affiliation_adult_list.exclude(coop_child_support__in=exclude_list)
        invalid_41s = Adult.objects.filter(family_affiliation__in=exclude_affiliation_list2).exclude(coop_child_support='')

        for invalid_41_affiliation in invalid_41_affiliations:
            self.create_validation_error('T1-042', '43', 'COOPERATION WITH CHILD SUPPORT','ITEM 43 MUST = 1-2, OR 9 ', 'FATAL', family=invalid_41_affiliation.family, adult=invalid_41_affiliation)

        for invalid_41 in invalid_41s:
            self.create_validation_error('T1-043', '43', 'COOPERATION WITH CHILD SUPPORT', 'IF ITEM 43 = BLANK, ITEM 30 MUST = 5', 'FATAL', family=invalid_41.family,adult=invalid_41)

    def validate_countable_federal_time_limit_months(self):
        #IF ITEM 30 = 1 AND ITEM 38=1 OR 2, THEN ITEM 44 MUST => 0
        exclude_list=['']
        invalidate_ftls = Adult.objects.filter(family_affiliation = 1, relationship_to_hoh__in=['01', '02'],countable_federal_time_limit_months__in=exclude_list)
        for invalidate_ftl in invalidate_ftls:
            print(invalidate_ftl)
            self.create_validation_error('T1-045', '44', 'NUMBER OF MONTHS COUNTABLE TOWARDS FEDERAL TIME-LIMIT', \
                        'IF ITEM 30 = 1 AND ITEM 38=1 OR 2, THEN ITEM 44 MUST => 0', 'FATAL',family=invalidate_ftl.family,adult=invalidate_ftl)

    def validate_employment_status(self):
        #IF ITEM 30 = 1-4 THEN ITEM 47 MUST = 1-3
        #IF ITEM 47 = BLANK, ITEM 30 MUST = 5
        exclude_list = [1,2,3]
        exclude_affiliation_list1 = [1,2,3,4]
        exclude_affiliation_list2 = [5]
        excluded_affiliation_adult_list = Adult.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_47_affiliations = excluded_affiliation_adult_list.exclude(employment_status__in=exclude_list)
        invalid_47s = Adult.objects.filter(employment_status='').exclude(family_affiliation__in=exclude_affiliation_list2)
        for invalid_47_affiliation in invalid_47_affiliations:
            self.create_validation_error('T1-050', '47', 'EMPLOYMENT STATUS', \
                        'IF ITEM 30 = 1-4 THEN ITEM 47 MUST = 1-3', 'FATAL',family=invalid_47_affiliation.family,adult=invalid_47_affiliation)
        
        for invalid_47 in invalid_47s:
            self.create_validation_error('T1-051', '47', 'EMPLOYMENT STATUS', 'IF ITEM 47 = BLANK, ITEM 30 MUST = 5', 'FATAL', family=invalid_47.family,adult=invalid_47)

    def validate_work_participation_status(self):
        #IF ITEM 30 = 1 or 2, THEN ITEM 49 MUST = 01-02, 05-19, or 99
        #IF ITEM 30 = 3, 4, or 5, THEN ITEM 49 MUST = 99, OR BLANK
        exclude_list1 = ['01', '02','05','06','07','08','09','10', '11','12','13','14','15','16','17','18','19','99']
        exclude_list2 = ['','99']
        wps_errors = Adult.objects.filter(family_affiliation__in=[1,2]).exclude(work_participation_status__in=exclude_list1)
        wps1_errors = Adult.objects.filter(family_affiliation__in=[3,4,5]).exclude(work_participation_status__in=exclude_list2)
        for wps_error in wps_errors:
            self.create_validation_error('T1-052', '49', 'WORK PARTICIPATION STATUS', \
                        'IF ITEM 30 = 1 or 2, THEN ITEM 49 MUST = 01-02, 05-19, or 99', 'FATAL', family=wps_error.family, adult=wps_error)
        for wps1_error in wps1_errors:
            self.create_validation_error('T1-053', '49', 'WORK PARTICIPATION STATUS', \
                        'IF ITEM 30 = 3, 4, or 5, THEN ITEM 49 MUST = 99, OR BLANK', 'FATAL', family=wps1_error.family,adult=wps1_error)

    def validate_work_activity_hours(self):
        #IF ITEM 30 = 1, THEN ITEM 50 MUST => 0
        work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], unsubsidized_employment_hours='', unsubsidized_employment_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error('T1-054', '50', 'UNSUBSIDIZED EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 50 MUST => 0', 'FATAL', family=work_activity_hour_error.family,adult=work_activity_hour_error)
        
        work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], unsubsidized_employment_hours='', unsubsidized_employment_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error(work_activity_hour_error.family.case_number,'T1-054', '50', 'UNSUBSIDIZED EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 50 MUST => 0', 'FATAL',family=work_activity_hour_error.family,adult=work_activity_hour_error)
        
        work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], subsidized_private_employment_hours='', subsidized_private_employment_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error('T1-055', '51', 'SUBSIDIZED PVT EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 51 MUST => 0', 'FATAL', family=work_activity_hour_error.family,adult=work_activity_hour_error)
        
        work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], subsidized_public_employment_hours='', subsidized_public_employment_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error('T1-056', '52', 'UNSUBSIDIZED EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 52 MUST => 0', 'FATAL',family=work_activity_hour_error.family,adult=work_activity_hour_error)
        
        work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], on_job_training_hours='', on_job_training_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error('T1-058', '54', 'UNSUBSIDIZED EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 54 MUST => 0', 'FATAL', family=work_activity_hour_error.family,adult=work_activity_hour_error)
        
            work_activity_hour_errors = Adult.objects.filter(family_affiliation__in=[1], unsubsidized_employment_hours='', unsubsidized_employment_hours__isnull=True)
        for work_activity_hour_error in work_activity_hour_errors:
            self.create_validation_error('T1-054', '50', 'UNSUBSIDIZED EMPLOYMENT', \
                        'IF ITEM 30 = 1, THEN ITEM 50 MUST => 0', 'FATAL',family=work_activity_hour_error.family,adult=work_activity_hour_error)
    
    def validate_child_family_affiliation(self):
        #ITEM 67 MUST = 1-5
        exclude_list = [1,2,3,4,5]
        invalid_affiliations = Child.objects.exclude(family_affiliation__in=exclude_list)
        for child in invalid_affiliations:
            self.create_validation_error('T1-070', '67', 'FAMILY AFFILIATION -CHILD', 'ITEM 67 MUST = 1-5', 'FATAL', family=child.family, adult=child)
    
    def validate_child_dob(self):
        #IF ITEM 68 = 99999999 THEN ITEM 67 MUST = 2-5 
        #ITEM 68 MUST NOT BE BLANK
        exclude_list = [2,3,4,5]
        children = Child.objects.filter(date_of_birth = '', date_of_birth__isnull=True)
        for child in children:
            self.create_validation_error('T1-071', '68', 'DATE OF BIRTH -CHILD', 'ITEM 68 MUST NOT BE BLANK OR ZEROES', 'FATAL', family=child.family, adult=child)

        children = Child.objects.filter(date_of_birth='99999999').exclude(family_affiliation__in=exclude_list)
        for child in children:
            self.create_validation_error('T1-072', '68', 'DATE OF BIRTH -CHILD', 'IF ITEM 68 = 99999999 ITEM 67 MUST = 2-5', 'FATAL',family=child.family, adult=child)

    def validate_child_ssn(self):
        #IF ITEM 69 = 999999999 THEN ITEM 67 MUST = 2-5
        #IF ITEM 69 = BLANK, ITEM 67 MUST = 4
        invalid_ssns = Adult.objects.filter(ssn='', ssn__isnull=True)
        invalid_ssn_affiliations= Child.objects.filter(ssn='999999999', family_affiliation=1)
        for invalid_ssn in invalid_ssns:
            self.create_validation_error('T1-073', '69', 'SSN -CHILD', 'ITEM 69 MUST NOT BE BLANK', 'FATAL', family=invalid_ssn.family, adult=invalid_ssn)

        for invalid_ssn_affiliation in invalid_ssn_affiliations:
            self.create_validation_error('T1-074', '69', 'SSN -ADULT', 'IF ITEM 69 = 999999999 ITEM 67 MUST = 2-5', 'FATAL', family=invalid_ssn_affiliation.family, adult=invalid_ssn_affiliation) 

    def validate_child_race_ethnicity(self):
        #IF ITEM 70A = BLANK ITEM 67 MUST = 4
        #IF ITEM 67= 1-3, ITEM 34A MUST = 1 OR 2
        exclude_list = [1,2]
        exclude_affiliation_list = [1,2,3]
        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34a_hispanic_latino__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34a_hispanic_latino='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-075', '70', 'RACE/ETHNICITY', \
                        'IF ITEM 70A = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-076', '70', 'RACE/ETHNICITY', \
                                    'IF ITEM 67= 1-3, ITEM 70A MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34b_american_indian_alaska_native__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34b_american_indian_alaska_native='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-077', '70', 'RACE/ETHNICITY', 'IF ITEM 70B = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:
                        self.create_validation_error('T1-078', '70', 'RACE/ETHNICITY', 'IF ITEM 67= 1-3, ITEM 70B MUST = 1 OR 2', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)
    
        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34c_asian__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34c_asian='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
            self.create_validation_error('T1-079', '70', 'RACE/ETHNICITY','IF ITEM 70C = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-079', '70', 'RACE/ETHNICITY', 'IF ITEM 67= 1-3, ITEM 70C MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34d_black__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34d_black='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:
                        self.create_validation_error('T1-080', '70', 'RACE/ETHNICITY','IF ITEM 70D = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)
        for invalid_race_affiliation in invalid_race_affiliations:        
            self.create_validation_error('T1-081', '70', 'RACE/ETHNICITY','IF ITEM 70D = BLANK ITEM 67 MUST = 4', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34e_native_pacific_islander__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34e_native_pacific_islander='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:        
            self.create_validation_error('T1-082', '70', 'RACE/ETHNICITY', 'IF ITEM 70E = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-083', '70', 'RACE/ETHNICITY', 'IF ITEM 67= 1-3, ITEM 70E MUST = 1 OR 2', 'FATAL', family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

        invalid_race_affiliations = Child.objects.filter(family_affiliation__in=exclude_affiliation_list).exclude(item34f_white__in = exclude_list)
        blank_race_affilitations = Child.objects.filter(item34f_white='', family_affiliation__in=exclude_affiliation_list)
        for blank_race_affilitation in blank_race_affilitations:        
            self.create_validation_error('T1-084', '70', 'RACE/ETHNICITY', 'IF ITEM 70F = BLANK ITEM 67 MUST = 4', 'FATAL', family=blank_race_affilitation.family, adult=blank_race_affilitation)            

        for invalid_race_affiliation in invalid_race_affiliations:
            self.create_validation_error('T1-085', '70', 'RACE/ETHNICITY', 'IF ITEM 67= 1-3, ITEM 67F MUST = 1 OR 2', 'FATAL',family=invalid_race_affiliation.family, adult=invalid_race_affiliation)

    def validate_child_relationship_to_hoh(self):
        #ITEM 73 MUST = 01-10
        exclude_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
        invalid_hoh_relations = Child.objects.exclude(relation_to_hoh__in=exclude_list)

        for invalid_hoh_relation in invalid_hoh_relations:
            self.create_validation_error('T1-087', '73', 'RELATIONSHIP TO HEAD OF HOUSEHOLD', 'ITEM 73 MUST = 01-10', 'FATAL', family=invalid_hoh_relation.family, adult=invalid_hoh_relation) 

    def validate_child_parent_with_minor(self):
        #IF ITEM 74 = BLANK THEN ITEM 67 MUST = 4-5
        #IF ITEM 67 = 1,2,3 ITEM 74 MUST = 1-3
        exclude_list = [1,2,3]
        exclude_affiliation_list1 = [1,2,3]
        exclude_affiliation_list2 = [4,5]
        invalid_39_affiliations = Child.objects.filter(parent_with_minor_child='', parent_with_minor_child__isnull=True, ).exclude(family_affiliation__in=exclude_affiliation_list2)
        invalid_39s = Child.objects.filter(family_affiliation__in=exclude_affiliation_list1).exclude(parent_with_minor_child__in=exclude_list)
        for invalid_39_affiliation in invalid_39_affiliations:
            self.create_validation_error('T1-088', '74', 'PARENT WITH MINOR CHILD IN THE FAMILY','IF ITEM 74 = BLANK, ITEM 67 MUST = 4 OR 5', 'FATAL', family=invalid_39_affiliation.family, adult=invalid_39_affiliation)
            
        for invalid_39 in invalid_39s:
            self.create_validation_error('T1-089', '74', 'PARENT WITH MINOR CHILD IN THE FAMILY', 'IF ITEM 67 = 1,2,3 , ITEM 74 MUST = 1-3', 'FATAL', family=invalid_39.family, adult=invalid_39)

    def validate_education_level(self):
        #IF ITEM 67 = 2,3,5 ITEM 75 MUST = 01-16,98,99
        #IF ITEM 67 = 1 ITEM 75 MUST = 01-16,98
        #IF ITEM 75 = BLANK, ITEM 67 MUST = 4
        exclude_list1 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '98', '99']
        exclude_list2 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '98', '99']
        exclude_affiliation_list1 = [2,3,4,5]
        exclude_affiliation_list2 = [1]
        exclude_affiliation_list3 = [1,2,3,4]
        excluded_affiliation_adult_list = Child.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_41_affiliations = excluded_affiliation_adult_list.exclude(educational_level__in=exclude_list1)
        invalid_41s = Child.objects.filter(family_affiliation__in=exclude_affiliation_list2).exclude(educational_level__in=exclude_list2)
        invalid_41bs = Child.objects.filter(educational_level=4).exclude(family_affiliation__in=exclude_affiliation_list3)
        for invalid_41_affiliation in invalid_41_affiliations:
            self.create_validation_error('T1-090', '75', 'EDUCATION LEVEL','IF ITEM 67 = 2-5 ITEM 75 MUST =? 01-16,98,99', 'FATAL', family=invalid_41_affiliation.family,adult=invalid_41_affiliation)

        for invalid_41 in invalid_41s:
            self.create_validation_error('T1-091', '75', 'EDUCATION LEVEL', 'IF ITEM 67 = 1, ITEM 75 MUST = 01-16,98', 'FATAL',family=invalid_41.family,adult=invalid_41)

        for invalid_41b in invalid_41bs:
            self.create_validation_error('T1-092', '75', 'EDUCATION LEVEL', 'IF ITEM 75 = BLANK, ITEM 67 MUST = 4', 'FATAL', family=invalid_41b.family, adult=invalid_41b)

    def validate_citizenship_immigration_status(self):
        #IF ITEM 76 = BLANK ITEM 67? MUST = 4
        #IF ITEM 67 = 1-3,5 ITEM 76 MUST = 1-2, OR 9
        exclude_list = [1,2,9]
        exclude_affiliation_list1 = [1,2,3,5]
        exclude_affiliation_list2 = [4]
        excluded_affiliation_adult_list = Child.objects.exclude(family_affiliation__in=exclude_affiliation_list1)
        invalid_39_affiliations = excluded_affiliation_adult_list.exclude(citizenship_immigration_status__in=exclude_list)
        invalid_39s = Child.objects.filter(family_affiliation__in=exclude_affiliation_list2).exclude(citizenship_immigration_status='')
        for invalid_39_affiliation in invalid_39_affiliations:
            self.create_validation_error('T1-093', '76', 'CITIZENSHIP/ALIENAGE','IF ITEM 76 = BLANK, ITEM 67? MUST = 4', 'FATAL', family=invalid_39_affiliation.family,adult=invalid_39_affiliation)
        
        for invalid_39 in invalid_39s:
            self.create_validation_error('T1-094', '76', 'CITIZENSHIP/ALIENAGE', 'IF ITEM 76 = 1-3,5, ITEM 42 MUST = 1-2,9', 'FATAL', family=invalid_39.family,adult=invalid_39)