from django.test import TestCase
from lrs import models
import json
from lrs.exceptions import ParamError, InvalidXML
from lrs.objects import Activity
import pdb

class ActivityModelsTests(TestCase):        
    #Called on all activity django models to see if they were created with the correct fields    
    def do_activity_model(self,realid,act_id, objType):
        self.assertEqual(models.activity.objects.filter(id=realid)[0].objectType, objType)
        self.assertEqual(models.activity.objects.filter(id=realid)[0].activity_id, act_id)

    #Called on all activity django models with definitions to see if they were created with the correct 
    # fields
    def do_activity_definition_model(self, fk,course, intType):
        act_def = models.activity_definition.objects.filter(activity=fk)[0]
        self.assertEqual(act_def.activity_definition_type, course)
        self.assertEqual(act_def.interactionType, intType)


    # Called on all activity django models with extensions to see if they were created with the correct 
    # fields and values. All extensions are created with the same three values and keys
    def do_activity_definition_extensions_model(self, def_fk, key1, key2, key3, value1, value2, value3):
        #Create list comprehesions to easier assess keys and values
        extList = models.activity_extensions.objects.values_list().filter(activity_definition=def_fk)
        extKeys = [ext[1] for ext in extList]
        extVals = [ext[2] for ext in extList]

        self.assertIn(key1, extKeys)
        self.assertIn(key2, extKeys)
        self.assertIn(key3, extKeys)
        self.assertIn(value1, extVals)
        self.assertIn(value2, extVals)
        self.assertIn(value3, extVals)

    #Called on all activity django models with a correctResponsePattern because of cmi.interaction type
    def do_activity_definition_correctResponsePattern_model(self, rsp_fk, answers):
        rspAnswers = models.correctresponsespattern_answer.objects.values_list('answer',
                     flat=True).filter(correctresponsespattern=rsp_fk)
        
        for answer in answers:
            self.assertIn(answer,rspAnswers)

    #Called on all activity django models with choices because of sequence and choice interactionType
    def do_actvity_definition_choices_model(self, def_fk, clist, dlist):
        # Grab all lang map IDs in act def
        desc_lang_maps = models.activity_definition_choice.objects.values_list('description',
                flat=True).filter(activity_definition=def_fk)
        
        # Recreate lang map and add to list for check
        lang_map_list = []
        for desc in desc_lang_maps:
            d = models.LanguageMap.objects.get(id=desc)
            tup = (d.key, d.value)
            lang_map_list.append(tup)

        choices = models.activity_definition_choice.objects.values_list('choice_id',
                flat=True).filter(activity_definition=def_fk)
        
        for c in clist:
            self.assertIn(c,choices)

        for d in dlist:
            self.assertIn(d, lang_map_list)

    #Called on all activity django models with scale because of likert interactionType
    def do_actvity_definition_likert_model(self, def_fk, clist, dlist):
        desc_lang_maps = models.activity_definition_scale.objects.values_list('description',
                flat=True).filter(activity_definition=def_fk)

        # Recreate lang map and add to list for check
        lang_map_list = []
        for desc in desc_lang_maps:
            d = models.LanguageMap.objects.get(id=desc)
            tup = (d.key, d.value)
            lang_map_list.append(tup)
        
        choices = models.activity_definition_scale.objects.values_list('scale_id',
                flat=True).filter(activity_definition=def_fk)
        
        for c in clist:
            self.assertIn(c,choices)

        for d in dlist:
            self.assertIn(d, lang_map_list)

    #Called on all activity django models with steps because of performance interactionType
    def do_actvity_definition_performance_model(self, def_fk, slist, dlist):
        desc_lang_maps = models.activity_definition_step.objects.values_list('description',
                flat=True).filter(activity_definition=def_fk)

        # Recreate lang map and add to list for check
        lang_map_list = []
        for desc in desc_lang_maps:
            d = models.LanguageMap.objects.get(id=desc)
            tup = (d.key, d.value)
            lang_map_list.append(tup)
        
        steps = models.activity_definition_step.objects.values_list('step_id',
            flat=True).filter(activity_definition=def_fk)
        
        for s in slist:
            self.assertIn(s,steps)

        for d in dlist:
            self.assertIn(d, lang_map_list)

    #Called on all activity django models with source and target because of matching interactionType
    def do_actvity_definition_matching_model(self, def_fk, source_id_list, source_desc_list,
                                             target_id_list, target_desc_list):

        source_desc_lang_maps = models.activity_definition_source.objects.values_list('description',
                flat=True).filter(activity_definition=def_fk)

        # Recreate lang map and add to list for check
        source_lang_map_list = []
        for desc in source_desc_lang_maps:
            d = models.LanguageMap.objects.get(id=desc)
            tup = (d.key, d.value)
            source_lang_map_list.append(tup)

        sources = models.activity_definition_source.objects.values_list('source_id',
                flat=True).filter(activity_definition=def_fk)
        
        target_desc_lang_maps = models.activity_definition_target.objects.values_list('description',
                flat=True).filter(activity_definition=def_fk)

        # Recreate lang map and add to list for check
        target_lang_map_list = []
        for desc in target_desc_lang_maps:
            d = models.LanguageMap.objects.get(id=desc)
            tup = (d.key, d.value)
            target_lang_map_list.append(tup)

        
        targets = models.activity_definition_target.objects.values_list('target_id',
                flat=True).filter(activity_definition=def_fk)
        
        for s_id in source_id_list:
            self.assertIn(s_id,sources)

        for s_desc in source_desc_list:
            self.assertIn(s_desc, source_lang_map_list)

        for t_id in target_id_list:
            self.assertIn(t_id,targets)

        for t_desc in target_desc_list:
            self.assertIn(t_desc, target_lang_map_list)            


    # Test activity that doesn't have a def, isn't a link and resolves (will not create Activity object)
    def test_activity_no_def_not_link_resolve(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
            'id': 'http://yahoo.com'}))

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
            activity_id='http://yahoo.com')

    # Test activity that doesn't have a def, isn't a link and doesn't resolve (creates useless 
    # Activity object)
    def test_activity_no_def_not_link_no_resolve(self):
        act = Activity.Activity(json.dumps({'objectType':'Activity', 'id':'foo'}))
        
        self.do_activity_model(act.activity.id, 'foo', 'Activity')

    # Test activity that doesn't have a def, isn't a link and conforms to schema
    # (populates everything from XML)
    def test_activity_no_def_not_link_schema_conform(self):
        act = Activity.Activity(json.dumps({'objectType':'Activity',
            'id': 'http://localhost:8000/TCAPI/tcexample/'}))

        fk = models.activity.objects.filter(id=act.activity.id)
        
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'Example Name')
        self.assertEqual(name_set[1].key, 'en-CH')
        self.assertEqual(name_set[1].value, 'Alt Name')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'Example Desc')
        self.assertEqual(desc_set[1].key, 'en-CH')
        self.assertEqual(desc_set[1].value, 'Alt Desc')

        self.do_activity_model(act.activity.id, 'http://localhost:8000/TCAPI/tcexample/', 'Activity')        
        self.do_activity_definition_model(fk, 'module','course')

    # Test activity that doesn't have a def, isn't a link and conforms to schema but ID already exists
    # (won't create it)
    def test_activity_no_def_not_link_schema_conform1(self):
        act = Activity.Activity(json.dumps({'objectType':'Activity',
            'id': 'http://localhost:8000/TCAPI/tcexample/'}))
        
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
            'id': 'http://localhost:8000/TCAPI/tcexample/'}))

    '''
    Choices is not part of the XML schema for now, so this will throw an exception
    # Test activity that doesn't have a def, isn't a link and conforms to schema with CRP
    # (populates everything from XML)
    def test_activity_no_def_not_link_schema_conform_correctResponsesPattern(self):
        act = Activity.Activity(json.dumps({'objectType':'Activity',
            'id': 'http://localhost:8000/TCAPI/tcexample3/'}))

        fk = models.activity.objects.filter(id=act.activity.id)
        def_fk = models.activity_definition.objects.filter(activity=fk)
        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=def_fk)

        self.do_activity_object(act,'http://localhost:8000/TCAPI/tcexample3/', 'Activity')
        self.do_activity_definition_object(act, 'Example Name', 'Example Desc', 'cmi.interaction',
            'choice')

        self.do_activity_model(act.activity.id, 'http://localhost:8000/TCAPI/tcexample3/', 'Activity')        
        self.do_activity_definition_model(fk, 'Example Name', 'Example Desc', 'cmi.interaction',
            'choice')
    
        self.assertEqual(act.answers[0].answer, 'golf')
        self.assertEqual(act.answers[1].answer, 'tetris')
        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['golf', 'tetris'])
    '''

    # Test activity that doesn't have a def, isn't a link and conforms to schema with extensions
    # (populates everything from XML)
    def test_activity_no_def_not_link_schema_conform_extensions(self):
        act = Activity.Activity(json.dumps({'objectType':'Activity',
            'id': 'http://localhost:8000/TCAPI/tcexample2/'}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-US')
        self.assertEqual(name_set[0].value, 'Example Name')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'Example Desc')

        self.do_activity_model(act.activity.id, 'http://localhost:8000/TCAPI/tcexample2/', 'Activity')        
        self.do_activity_definition_model(fk, 'module','course')

        self.do_activity_definition_extensions_model(act_def, 'keya', 'keyb', 'keyc','first value',
            'second value', 'third value')

    # Test an activity that has a def,is not a link yet the ID resolves, but doesn't conform to XML schema
    # (will not create one)
    def test_activity_not_link_resolve(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
                'id': 'http://tincanapi.wikispaces.com','definition': {'name': {'en-US':'testname'},
                'description': {'en-US':'testdesc'}, 'type': 'course','interactionType': 'intType'}}))

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
            activity_id='http://tincanapi.wikispaces.com')

    # Test an activity that has a def, not a link and the provided ID doesn't resolve
    # (should still use values from JSON)
    def test_activity_not_link_no_resolve(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity',
                'id':'/var/www/adllrs/activity/example.xml','definition': {'name': {'en-CH':'testname'},
                'description': {'en-US':'testdesc'}, 'type': 'course','interactionType': 'intType'}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-CH')
        self.assertEqual(name_set[0].value, 'testname')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'testdesc')

        self.do_activity_model(act.activity.id, '/var/www/adllrs/activity/example.xml', 'Activity')        
        self.do_activity_definition_model(fk, 'course', 'intType')

    # Test an activity that has a def, not a link and the provided ID conforms to the schema
    # (should use values from XML and override JSON)
    def test_activity_not_link_schema_conform(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity',
                'id':'http://localhost:8000/TCAPI/tcexample4/','definition': {'name': {'en-FR': 'name'},
                'description': {'en-FR':'desc'}, 'type': 'course','interactionType': 'intType'}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-US')
        self.assertEqual(name_set[0].value, 'Example Name')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'Example Desc')

        self.do_activity_model(act.activity.id, 'http://localhost:8000/TCAPI/tcexample4/', 'Activity')        
        self.do_activity_definition_model(fk, 'module','course')

    #Test an activity that has a def, is a link and the ID resolves (should use values from JSON)
    def test_activity_link_resolve(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id': 'http://localhost:8000/TCAPI/',
                'definition': {'name': {'en-GB':'testname'},'description': {'en-GB':'testdesc1'},
                'type': 'link','interactionType': 'intType'}}))


        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-GB')
        self.assertEqual(name_set[0].value, 'testname')

        self.assertEqual(desc_set[0].key, 'en-GB')
        self.assertEqual(desc_set[0].value, 'testdesc1')

        self.do_activity_model(act.activity.id, 'http://localhost:8000/TCAPI/', 'Activity')        
        self.do_activity_definition_model(fk, 'link', 'intType')

    #Test an activity that has a def, is a link and the ID does not resolve (will not create one)
    def test_activity_link_no_resolve(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity', 
                'id': 'http://foo','definition': {'name': {'en-GB':'testname'},
                'description': {'en-GB':'testdesc'}, 'type': 'link','interactionType': 'intType'}}))

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
                activity_id='http://foo')

    #Throws exception because incoming data is not JSON
    def test_activity_not_json(self):
        self.assertRaises(ParamError, Activity.Activity,
            "This string should throw exception since it's not JSON")

    #Test an activity where there is no given objectType, won't be created with one
    def test_activity_no_objectType(self):
        act = Activity.Activity(json.dumps({'id':'fooa'}))
        
        self.do_activity_model(act.activity.id,'fooa', None)

    # Test an activity with a provided objectType - defaults to Activity
    def test_activity_wrong_objectType(self):
        act = Activity.Activity(json.dumps({'id': 'foob', 'objectType':'Wrong'}))    

        self.do_activity_model(act.activity.id, 'foob', 'Activity')

    #Test activity where given URL doesn't resolve
    def test_activity_invalid_activity_id(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'id': 'http://foo',
                'objectType':'Activity','definition': {'name': {'en-GB':'testname'},
                'description': {'en-GB':'testdesc'}, 'type': 'link','interactionType': 'intType'}}))

    #Test activity with definition - must retrieve activity object in order to test definition from DB
    def test_activity_definition(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'fooc',
                'definition': {'name': {'en-GB':'testname'},'description': {'en-US':'testdesc'}, 
                'type': 'course','interactionType': 'intType'}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-GB')
        self.assertEqual(name_set[0].value, 'testname')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'testdesc')

        self.do_activity_model(act.activity.id,'fooc', 'Activity')        
        self.do_activity_definition_model(fk, 'course', 'intType')

    #Test activity with definition given wrong type (won't create it)
    def test_activity_definition_wrong_type(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
                'id':'http://msn.com','definition': {'NAME': {'en-CH':'testname'},
                'descripTION': {'en-CH':'testdesc'}, 'tYpe': 'wrong','interactionType': 'intType'}}))

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
            activity_id='http://msn.com')
    
    #Test activity with definition missing name in definition (won't create it)
    def test_activity_definition_required_fields(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
                'id':'http://google.com','definition': {'description': {'en-CH':'testdesc'},
                'type': 'wrong','interactionType': 'intType'}}))

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
            activity_id='http://google.com')

    # Test activity with definition that contains extensions - need to retrieve activity and activity definition objects
    # in order to test extenstions
    def test_activity_definition_extensions(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'food',
                'definition': {'name': {'en-FR':'testname2'},'description': {'en-CH':'testdesc2'},
                'type': 'course','interactionType': 'intType2', 'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-CH')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        self.do_activity_model(act.activity.id,'food', 'Activity')        
        self.do_activity_definition_model(fk, 'course','intType2')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                'value3')

    def test_multiple_names_and_descs(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'food',
                'definition': {'name': {'en-FR':'testname2','en-US': 'testnameEN'},'description': {'en-CH':'testdesc2',
                'en-GB': 'testdescGB'},'type': 'course','interactionType': 'intType2', 'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        def_fk = models.activity_definition.objects.filter(activity=fk)

        name_set = def_fk[0].name.all()
        desc_set = def_fk[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-US')
        self.assertEqual(name_set[0].value, 'testnameEN')
        self.assertEqual(name_set[1].key, 'en-FR')
        self.assertEqual(name_set[1].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-GB')
        self.assertEqual(desc_set[0].value, 'testdescGB')
        self.assertEqual(desc_set[1].key, 'en-CH')
        self.assertEqual(desc_set[1].value, 'testdesc2')

        self.do_activity_model(act.activity.id,'food', 'Activity')        
        self.do_activity_definition_model(fk, 'course', 'intType2')

        self.do_activity_definition_extensions_model(def_fk, 'key1', 'key2', 'key3', 'value1', 'value2',
                'value3')


    #Test activity with definition given wrong interactionType (won't create one)
    def test_activity_definition_wrong_interactionType(self):

        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity', 
                'id':'http://facebook.com','definition': {'name': {'en-US':'testname2'},
                'description': {'en-GB':'testdesc2'}, 'type': 'cmi.interaction',
                'interactionType': 'intType2', 'correctResponsesPatteRN': 'response',
                'extensions': {'key1': 'value1', 'key2': 'value2','key3': 'value3'}}}))
     
        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
                          activity_id='http://facebook.com')

    #Test activity with definition and valid interactionType-it must also provide the
    # correctResponsesPattern field (wont' create it)
    def test_activity_definition_no_correctResponsesPattern(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity',
                'id':'http://twitter.com','definition': {'name': {'en-US':'testname2'},
                'description': {'en-CH':'testdesc2'},'type': 'cmi.interaction',
                'interactionType': 'true-false', 'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))
     
        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
                          activity_id='http://twitter.com')

    #Test activity with definition that is cmi.interaction and true-false interactionType
    def test_activity_definition_cmiInteraction_true_false(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'fooe',
                'definition': {'name': {'en-FR':'testname2'},'description': {'en-US':'testdesc2'}, 
                'type': 'cmi.interaction','interactionType': 'true-false',
                'correctResponsesPattern': ['true'] ,'extensions': {'key1': 'value1', 'key2': 'value2',
                'key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'testdesc2')        

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id,'fooe', 'Activity')                
        self.do_activity_definition_model(fk, 'cmi.interaction','true-false')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1',
                                                    'value2', 'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['true'])
    
    #Test activity with definition that is cmi.interaction and multiple choice interactionType
    def test_activity_definition_cmiInteraction_multiple_choice(self):    
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'foof',
                'definition': {'name': {'en-US':'testname1'},'description': {'en-US':'testdesc1'},
                'type': 'cmi.interaction','interactionType': 'choice',
                'correctResponsesPattern': ['golf', 'tetris'],'choices':[{'id': 'golf', 
                'description': {'en-US':'Golf Example', 'en-GB': 'GOLF'}},{'id': 'tetris',
                'description':{'en-US': 'Tetris Example', 'en-GB': 'TETRIS'}}, {'id':'facebook', 
                'description':{'en-US':'Facebook App', 'en-GB': 'FACEBOOK'}},{'id':'scrabble', 
                'description': {'en-US': 'Scrabble Example', 'en-GB': 'SCRABBLE'}}],'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-US')
        self.assertEqual(name_set[0].value, 'testname1')

        self.assertEqual(desc_set[0].key, 'en-US')
        self.assertEqual(desc_set[0].value, 'testdesc1')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id,'foof', 'Activity')
        self.do_activity_definition_model(fk, 'cmi.interaction', 'choice')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                                                     'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['golf', 'tetris'])
        
        #Check model choice values
        clist = ['golf', 'tetris', 'facebook', 'scrabble']
        dlist = [("en-US","Golf Example"),("en-US", "Tetris Example"),("en-US", "Facebook App"),
                 ("en-US", "Scrabble Example"), ('en-GB','GOLF'), ('en-GB', 'TETRIS'), ('en-GB', 'FACEBOOK'),
                 ('en-GB', 'SCRABBLE')]

        self.do_actvity_definition_choices_model(act_def, clist, dlist)        
        
    #Test activity with definition that is cmi.interaction and multiple choice but missing choices (won't create it)
    def test_activity_definition_cmiInteraction_multiple_choice_no_choices(self):
        self.assertRaises(ParamError, Activity.Activity, json.dumps({'objectType': 'Activity', 
                'id':'http://wikipedia.org','definition': {'name': {'en-US':'testname2'},
                'description': {'en-US':'testdesc2'},'type': 'cmi.interaction',
                'interactionType': 'choice','correctResponsesPattern': ['golf', 'tetris'],
                'extensions': {'key1': 'value1', 'key2': 'value2','key3': 'value3'}}}))   

        self.assertRaises(models.activity.DoesNotExist, models.activity.objects.get,
                activity_id='http://wikipedia.org')
    
    #Test activity with definition that is cmi.interaction and fill in interactionType
    def test_activity_definition_cmiInteraction_fill_in(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'foog',
                'definition': {'name': {'en-FR':'testname2'},'description': {'en-FR':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'fill-in',
                'correctResponsesPattern': ['Fill in answer'],'extensions': {'key1': 'value1',
                'key2': 'value2', 'key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-FR')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id,'foog', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction','fill-in')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                                                    'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['Fill in answer'])

    #Test activity with definition that is cmi.interaction and long fill in interactionType
    def test_activity_definition_cmiInteraction_long_fill_in(self):

        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'fooh',
                'definition': {'name': {'en-FR':'testname2'},'description': {'en-FR':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'fill-in',
                'correctResponsesPattern': ['Long fill in answer'],'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-FR')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'fooh', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction','fill-in')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                                                     'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['Long fill in answer'])

    #Test activity with definition that is cmi.interaction and likert interactionType
    def test_activity_definition_cmiInteraction_likert(self):    
        act = Activity.Activity(json.dumps({'objectType': 'Still gonna be activity', 'id':'fooi',
                'definition': {'name': {'en-CH':'testname2'},'description': {'en-CH':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'likert',
                'correctResponsesPattern': ['likert_3'],'scale':[{'id': 'likert_0',
                'description': {'en-US':'Its OK', 'en-GB': 'Tis OK'}},{'id': 'likert_1',
                'description':{'en-US': 'Its Pretty Cool', 'en-GB':'Tis Pretty Cool'}}, {'id':'likert_2',
                'description':{'en-US':'Its Cool Cool', 'en-GB':'Tis Cool Cool'}},
                {'id':'likert_3', 'description': {'en-US': 'Its Gonna Change the World'}}]}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-CH')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-CH')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'fooi', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'likert')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['likert_3'])

        #Check model choice values
        clist = ['likert_3']
        dlist = [("en-US", "Its OK"),("en-US", "Its Pretty Cool"), ("en-US", "Its Cool Cool"),
                 ("en-US", "Its Gonna Change the World"), ('en-GB', 'Tis OK'), ('en-GB', 'Tis Pretty Cool'),
                 ('en-GB', 'Tis Cool Cool')]
        
        self.do_actvity_definition_likert_model(act_def, clist, dlist)

    #Test activity with definition that is cmi.interaction and matching interactionType
    def test_activity_definition_cmiInteraction_matching(self):    
        act = Activity.Activity(json.dumps({'objectType': 'Still gonna be activity', 'id':'fooj',
                'definition': {'name': {'en-CH':'testname2'},'description': {'en-CH':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'matching',
                'correctResponsesPattern': ['lou.3,tom.2,andy.1'],'source':[{'id': 'lou',
                'description': {'en-US':'Lou', 'it': 'Luigi'}},{'id': 'tom','description':{'en-US': 'Tom', 'it':'Tim'}},
                {'id':'andy', 'description':{'en-US':'Andy'}}],'target':[{'id':'1',
                'description':{'en-US': 'SCORM Engine'}},{'id':'2','description':{'en-US': 'Pure-sewage'}},
                {'id':'3', 'description':{'en-US': 'SCORM Cloud', 'en-CH': 'cloud'}}]}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-CH')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-CH')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'fooj', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'matching')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['lou.3,tom.2,andy.1'])

        #Check model choice values
        source_id_list = ['lou', 'tom', 'andy']
        source_desc_list = [("en-US", "Lou"),("en-US", "Tom"),("en-US", "Andy"),('it', 'Luigi'), ('it', 'Tim')]
        target_id_list = ['1','2','3']
        target_desc_list = [("en-US", "SCORM Engine"),("en-US", "Pure-sewage"),
                            ("en-US", "SCORM Cloud"), ('en-CH', 'cloud') ]
        self.do_actvity_definition_matching_model(act_def, source_id_list, source_desc_list,
                                                  target_id_list, target_desc_list)

    #Test activity with definition that is cmi.interaction and performance interactionType
    def test_activity_definition_cmiInteraction_performance(self):    
        act = Activity.Activity(json.dumps({'objectType': 'activity', 'id':'fook',
                'definition': {'name': {'en-us':'testname2'},'description': {'en-us':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'performance',
                'correctResponsesPattern': ['pong.1,dg.10,lunch.4'],'steps':[{'id': 'pong',
                'description': {'en-US':'Net pong matches won', 'en-GB': 'won'}},{'id': 'dg',
                'description':{'en-US': 'Strokes over par in disc golf at Liberty'}},
                {'id':'lunch', 'description':{'en-US':'Lunch having been eaten'}}]}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-us')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-us')
        self.assertEqual(desc_set[0].value, 'testdesc2')        
        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'fook', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'performance')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['pong.1,dg.10,lunch.4'])

        #Check model choice values
        slist = ['pong', 'dg', 'lunch']
        dlist = [("en-US", "Net pong matches won"),("en-US", "Strokes over par in disc golf at Liberty"),
                 ("en-US", "Lunch having been eaten"), ('en-GB', 'won')]
        
        self.do_actvity_definition_performance_model(act_def, slist, dlist)

    # Test activity with definition that is cmi.interaction and sequencing interactionType
    def test_activity_definition_cmiInteraction_sequencing(self):    
        act = Activity.Activity(json.dumps({'objectType': 'activity', 'id':'fool',
                'definition': {'name': {'en-GB':'testname2'},'description': {'en-GB':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'sequencing',
                'correctResponsesPattern': ['lou,tom,andy,aaron'],'choices':[{'id': 'lou',
                'description': {'en-US':'Lou'}},{'id': 'tom','description':{'en-US': 'Tom'}},
                {'id':'andy', 'description':{'en-US':'Andy'}},{'id':'aaron',
                'description':{'en-US':'Aaron', 'en-GB': 'Erin'}}]}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-GB')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-GB')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'fool', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'sequencing')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['lou,tom,andy,aaron'])

        #Check model choice values
        clist = ['lou', 'tom', 'andy', 'aaron']
        dlist = [("en-US", "Lou"),("en-US", "Tom"),("en-US", "Andy"), ("en-US", "Aaron"), ('en-GB', 'Erin')]
        self.do_actvity_definition_choices_model(act_def, clist, dlist)

    #Test activity with definition that is cmi.interaction and numeric interactionType
    def test_activity_definition_cmiInteraction_numeric(self):

        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id':'foom',
                'definition': {'name': {'en-CH':'testname2'},'description': {'en-CH':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'numeric','correctResponsesPattern': ['4'],
                'extensions': {'key1': 'value1', 'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-CH')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-CH')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'foom', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'numeric')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                                                     'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['4'])

    #Test activity with definition that is cmi.interaction and other interactionType
    def test_activity_definition_cmiInteraction_other(self):

        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id': 'foon',
                'definition': {'name': {'en-FR':'testname2'},'description': {'en-FR':'testdesc2'},
                'type': 'cmi.interaction','interactionType': 'other',
                'correctResponsesPattern': ['(35.937432,-86.868896)'],'extensions': {'key1': 'value1',
                'key2': 'value2','key3': 'value3'}}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-FR')
        self.assertEqual(name_set[0].value, 'testname2')

        self.assertEqual(desc_set[0].key, 'en-FR')
        self.assertEqual(desc_set[0].value, 'testdesc2')

        rsp_fk = models.activity_def_correctresponsespattern.objects.filter(activity_definition=act_def)

        self.do_activity_model(act.activity.id, 'foon', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'other')

        self.do_activity_definition_extensions_model(act_def, 'key1', 'key2', 'key3', 'value1', 'value2',
                                                     'value3')

        self.do_activity_definition_correctResponsePattern_model(rsp_fk, ['(35.937432,-86.868896)'])

    # Should be the same, no auth required
    def test_multiple_activities(self):
        act1 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob'}))
        act2 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob'}))
        act3 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob'}))
        act4 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foon'}))

        self.assertEqual(act1.activity.id, act2.activity.id)
        self.assertEqual(act1.activity.id, act3.activity.id)
        self.assertEqual(act2.activity.id, act3.activity.id)
        self.assertNotEqual(act1.activity.id, act4.activity.id)

    def test_language_map_description_name(self):
        act = Activity.Activity(json.dumps({'objectType': 'Activity', 'id': 'foz',
                'definition': {'name': {'en-US':'actname'},'description': {'en-us':'actdesc'},
                'type': 'cmi.interaction','interactionType': 'other',
                    'correctResponsesPattern': ['(35,-86)']}}))

        fk = models.activity.objects.filter(id=act.activity.id)
        act_def = models.activity_definition.objects.filter(activity=fk)

        name_set = act_def[0].name.all()
        desc_set = act_def[0].description.all()
        

        self.assertEqual(name_set[0].key, 'en-US')
        self.assertEqual(name_set[0].value, 'actname')

        self.assertEqual(desc_set[0].key, 'en-us')
        self.assertEqual(desc_set[0].value, 'actdesc')
        self.do_activity_model(act.activity.id, 'foz', 'Activity')

        self.do_activity_definition_model(fk, 'cmi.interaction', 'other')

    def test_multiple_activities_update_name(self):
        act1 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-US':'actname'},'description': {'en-us':'actdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))
        
        act2 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-US':'actname2'},'description': {'en-us':'actdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))

        fk1 = models.activity.objects.filter(id=act1.activity.id)[0]
        self.do_activity_model(act1.activity.id, 'foob', 'Activity')
        act_def1 = models.activity_definition.objects.filter(activity=fk1)

        name_set1 = act_def1[0].name.all()
        desc_set1 = act_def1[0].description.all()
        

        self.assertEqual(name_set1[0].key, 'en-US')
        self.assertEqual(name_set1[0].value, 'actname2')

        self.assertEqual(desc_set1[0].key, 'en-us')
        self.assertEqual(desc_set1[0].value, 'actdesc')        


        self.do_activity_definition_model(fk1, 'cmi.interaction', 'other')

        fk2 = models.activity.objects.filter(id=act2.activity.id)[0]
        self.do_activity_model(act2.activity.id, 'foob', 'Activity')
        act_def2 = models.activity_definition.objects.filter(activity=fk2)

        name_set2 = act_def2[0].name.all()
        desc_set2 = act_def2[0].description.all()
        

        self.assertEqual(name_set2[0].key, 'en-US')
        self.assertEqual(name_set2[0].value, 'actname2')

        self.assertEqual(desc_set2[0].key, 'en-us')
        self.assertEqual(desc_set2[0].value, 'actdesc')        
        self.do_activity_definition_model(fk2, 'cmi.interaction', 'other')

        self.assertEqual(act1.activity, act2.activity)
        self.assertEqual(fk1.activity_definition, fk2.activity_definition)

        # __contains makes the filter case sensitive
        self.assertEqual(len(models.LanguageMap.objects.filter(key__contains = 'en-US')), 1)

        # Should only have 2 total
        self.assertEqual(len(models.LanguageMap.objects.all()), 2)
        
    def test_multiple_activities_update_desc(self):
        act1 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foobe',
            'definition':{'name': {'en-US':'actname'},'description': {'en-us':'actdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))
        
        act2 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foobe',
            'definition':{'name': {'en-US':'actname'},'description': {'en-us':'actdesc2'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))

        fk1 = models.activity.objects.filter(id=act1.activity.id)[0]
        self.do_activity_model(act1.activity.id, 'foobe', 'Activity')
        act_def1 = models.activity_definition.objects.get(activity=fk1)

        name_set1 = act_def1.name.all()
        desc_set1 = act_def1.description.all()
        

        self.assertEqual(name_set1[0].key, 'en-US')
        self.assertEqual(name_set1[0].value, 'actname')

        self.assertEqual(desc_set1[0].key, 'en-us')
        self.assertEqual(desc_set1[0].value, 'actdesc2')        
        self.do_activity_definition_model(fk1, 'cmi.interaction', 'other')

        fk2 = models.activity.objects.filter(id=act2.activity.id)[0]
        self.do_activity_model(act2.activity.id, 'foobe', 'Activity')
        act_def2 = models.activity_definition.objects.get(activity=fk2)

        name_set2 = act_def2.name.all()
        desc_set2 = act_def2.description.all()
        
        self.assertEqual(name_set2[0].key, 'en-US')
        self.assertEqual(name_set2[0].value, 'actname')

        self.assertEqual(desc_set2[0].key, 'en-us')
        self.assertEqual(desc_set2[0].value, 'actdesc2')        
        self.do_activity_definition_model(fk2, 'cmi.interaction', 'other')

        self.do_activity_definition_model(fk2, 'cmi.interaction', 'other')

        self.assertEqual(act1.activity, act2.activity)
        self.assertEqual(fk1.activity_definition, fk2.activity_definition)

        # __contains makes the filter case sensitive, no models with en-US should be stored
        self.assertEqual(len(models.LanguageMap.objects.filter(key__contains = 'en-US')), 1)

        # Should only have 2 total
        self.assertEqual(len(models.LanguageMap.objects.all()), 2)

    def test_multiple_activities_update_both(self):
        act1 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-CH':'actname'},'description': {'en-FR':'actdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))
        
        act2 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-CH':'actname2'},'description': {'en-FR':'actdesc2'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))

        fk1 = models.activity.objects.filter(id=act1.activity.id)[0]
        self.do_activity_model(act1.activity.id, 'foob', 'Activity')
        act_def1 = models.activity_definition.objects.filter(activity=fk1)

        name_set1 = act_def1[0].name.all()
        desc_set1 = act_def1[0].description.all()
        

        self.assertEqual(name_set1[0].key, 'en-CH')
        self.assertEqual(name_set1[0].value, 'actname2')

        self.assertEqual(desc_set1[0].key, 'en-FR')
        self.assertEqual(desc_set1[0].value, 'actdesc2')

        self.do_activity_definition_model(fk1, 'cmi.interaction', 'other')

        fk2 = models.activity.objects.filter(id=act2.activity.id)[0]
        self.do_activity_model(act2.activity.id, 'foob', 'Activity')
        act_def2 = models.activity_definition.objects.filter(activity=fk2)

        name_set2 = act_def2[0].name.all()
        desc_set2 = act_def2[0].description.all()
        

        self.assertEqual(name_set2[0].key, 'en-CH')
        self.assertEqual(name_set2[0].value, 'actname2')

        self.assertEqual(desc_set2[0].key, 'en-FR')
        self.assertEqual(desc_set2[0].value, 'actdesc2')         
        self.do_activity_definition_model(fk2,'cmi.interaction', 'other')

        self.assertEqual(act1.activity, act2.activity)
        self.assertEqual(fk1.activity_definition, fk2.activity_definition)

        # __contains makes the filter case sensitive, no models with en-US should be stored
        self.assertEqual(len(models.LanguageMap.objects.filter(key__contains = 'en-US')), 0)
        
        # Should only have 2 total
        self.assertEqual(len(models.LanguageMap.objects.all()), 2)

    # When you switch to postgres backend, it saves the lang maps in the opposite order (just switch index in array) 
    def test_multiple_activities_update_both_and_add(self):
        act1 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-CH':'actname'},'description': {'en-FR':'actdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))
        
        act2 = Activity.Activity(json.dumps({'objectType':'Activity', 'id': 'foob',
            'definition':{'name': {'en-CH':'actname2', 'en-US': 'altname'},'description': {'en-FR':'actdesc2', 'en-GB': 'altdesc'}, 
            'type': 'cmi.interaction','interactionType': 'other','correctResponsesPattern': ['(35,-86)']}}))

        fk1 = models.activity.objects.filter(id=act1.activity.id)[0]
        self.do_activity_model(act1.activity.id, 'foob', 'Activity')
        act_def1 = models.activity_definition.objects.filter(activity=fk1)

        name_set1 = act_def1[0].name.all()
        desc_set1 = act_def1[0].description.all()
        
        self.assertEqual(name_set1[1].key, 'en-CH')
        self.assertEqual(name_set1[1].value, 'actname2')
        self.assertEqual(name_set1[0].key, 'en-US')
        self.assertEqual(name_set1[0].value, 'altname')

        self.assertEqual(desc_set1[1].key, 'en-FR')
        self.assertEqual(desc_set1[1].value, 'actdesc2')
        self.assertEqual(desc_set1[0].key, 'en-GB')
        self.assertEqual(desc_set1[0].value, 'altdesc')


        self.do_activity_definition_model(fk1, 'cmi.interaction', 'other')

        fk2 = models.activity.objects.filter(id=act2.activity.id)[0]
        self.do_activity_model(act2.activity.id, 'foob', 'Activity')
        act_def2 = models.activity_definition.objects.filter(activity=fk2)

        name_set2 = act_def2[0].name.all()
        desc_set2 = act_def2[0].description.all()
        

        self.assertEqual(name_set2[1].key, 'en-CH')
        self.assertEqual(name_set2[1].value, 'actname2')
        self.assertEqual(name_set2[0].key, 'en-US')
        self.assertEqual(name_set2[0].value, 'altname')

        self.assertEqual(desc_set2[1].key, 'en-FR')
        self.assertEqual(desc_set2[1].value, 'actdesc2')         
        self.assertEqual(desc_set2[0].key, 'en-GB')
        self.assertEqual(desc_set2[0].value, 'altdesc')

        self.do_activity_definition_model(fk2,'cmi.interaction', 'other')

        self.assertEqual(act1.activity, act2.activity)
        self.assertEqual(fk1.activity_definition, fk2.activity_definition)

        # __contains makes the filter case sensitive
        self.assertEqual(len(models.LanguageMap.objects.filter(key__contains = 'en-US')), 1)
        
        # Should only have 4 total
        self.assertEqual(len(models.LanguageMap.objects.all()), 4)
        

