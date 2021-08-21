# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Task Timer",
    
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",
        
    "version": "9.0.2",
    
    "category": "Project",
    
    "summary": "This module allow user to start/stop time of task.",
        
    "description": """ This module allow user to start/stop time of task. Easy to calculate duration of time taken for task. """,
     
    "depends": ['base','project','hr_timesheet_sheet','analytic'],
    
    "data": [
        'security/ir.model.access.csv',
        'views/project_task_time.xml',
    ],    
    
    "images": ["static/description/background.png",],
                 
    "installable": True,
    "auto_install": False,
    "application": True,  
      
    "price": "9",
    "currency": "EUR"          
}
