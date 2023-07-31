import math
import os
import time
import webbrowser

from fpdf import FPDF

import alien
import please
import mutations
import vocation
import table

# todo RP combat block: weak strong cannon fodder, canon fodder and canonical
# todo proficiency slot with actual weapons

def outputs_workflow(outputter:table.PersonaRecord, out_type: str) -> None:
    '''
    divides outputs between screen and pdf
    pdf has been rationalized for all families
    screen has not 
    '''
    family_type = outputter.FAMILY

    if out_type == "pdf":
        pdf_output_chooser(outputter)
    elif family_type == 'Toy':
        input("this doesn't exist yet!")
        please.say_goodnight_marsha
    elif family_type == "Anthro" and out_type == "screen":
        anthro_screen(outputter)  
    elif family_type == "Alien" and out_type == "screen":
        alien_screen(outputter)
    elif family_type == "Robot" and out_type == "screen":
        robot_screen(outputter)

    return None

################################################
#
# laws of fpdf
#
################################################
'''
US LETTER =
origin point = (0, 0) = top-left corner
x-coordinate increases moves right =  width = 215.9 = self.epw = effective page width
y-coordinate increases moves down  = height = 279.4 = self.eph = effective page height

LINE SAFETY:
1) set x,y start point outside of functions
2) only alter position in function if multiline 

numbers are  mm (millimeters) NOT pixels
font size is in points 1/72 of an inch
there are 25.4 mm in 1 inch
12 point font is 4.23 mm
arial 12 space = 1.8 mm 

def convert_points_to_mm(font_size_points):
    inches = font_size_points / 72  # convert points to inches
    mm = inches * 25.4  # convert inches to mm
    return mm


to center a circle abscissa and ordinate represent a bounding box not x,y center of circle
self.circle(
    (x - radius / 2),
    (y - radius / 2),
    radius,
    "D",
        )

and... 

Parameters for line: (x1, y1, x2, y2) where (x1, y1) is start point and (x2, y2) is end point
self.line(50, 50, 70, 70)  # Line 1: from point (50, 50) to point (70, 70)
self.line(50, 70, 70, 50)  # Line 2: from point (50, 70) to point (70, 50)
is a cross over

### testing management 
pdf.locutus() # puts a target where xy is 
pdf.center_line() # puts full page targe at page center

### display the build PDF
pdf.output(
    name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
    dest="F",
)
show_pdf()
'''

################################################
#
# classes for pdf creation
#
################################################

class PDF(FPDF):

    def perimiter_box(self)->None:
        '''
        draws a rectangle around entire page 
        must be called last for z value coverage
        '''
        self.set_draw_color(0, 0, 0) 
        self.set_line_width(1)
        self.rect(5, 13, (self.epw - 10), (self.eph - 20), "D")

    def title_line(self, persona, title_name: str = 'PERSONA') -> None:
        '''
        prints the top line title above the perimeter box 
        '''
        blob_left =f"**{title_name.upper()} RECORD** for {persona.Persona_Name}"
        blob_right = f"**Player:** {persona.Player_Name}"
        x=3.3
        y=4

        # print out PERSONA NAME BIG and LEFT justified
        self.print_MD_string(blob_left,18,x,y)

        # print out PLAYER NAME Small and RIGHT justified
        self.set_xy(3.3,6.3) # y adjust smaller font
        self.set_font("helvetica","", 12)
        right_most = self.epw - 10
        self.cell(
            w=(right_most),
            markdown=True,
            txt=blob_right,
            fill=False,
            border=False,
            align="R",
        )

    def data_footer(self, persona):
        '''
        prints the info at page bottom outside perimeter box
        '''
        self.set_font("Helvetica", size=7)
        line_height = self.font_size * 1.6
        self.set_xy(8, 273)
        persona.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())
        blob = f" **Printed:** {persona.Date_Updated} **Created:** {persona.Date_Created} **ID:** {persona.ID}"

        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
            align="C",
        )

    def description_line(self, persona,x:float = 0, y:float=0) -> float:
        '''
        prints  description of the persona
        '''

        if persona.FAMILY == "Anthro":
            blob = f"{persona.Persona_Name} is a {persona.Age} year-old {persona.FAMILY_TYPE} {persona.FAMILY_SUB.lower()} {persona.Vocation.lower()}."
        elif persona.FAMILY == "Alien":
            blob = f"{persona.Persona_Name} is a {persona.Quick_Description}"
        elif persona.FAMILY == "Robot":
            blob = f"{persona.Persona_Name} is a {persona.Description}"
        else:
            blob = "ERROR: No description for this persona"

        self.print_MD_string(blob,14,x,y)
        return y

    def attributes_lines(self, persona, x:float=0,y:float=0)->None:
        '''
        prints the three attribute lines: acronym, value, long form
        '''

        self.set_xy(x,y)
        ### title box 
        self.grey_box_title('ATTRIBUTES',5,y)

        ### description line
        x += self.get_string_width('ATTRIBUTES')
        self.set_xy(x,y)
        self.description_line(persona,x,y)

        ### [0] acronym and styling align-style, [1] long and center, [2] Prime for bot
        attribute_formatting = [
                ("**AWE**","Awareness",False),
                ("**CHA**","Charisma",False),
                ("**CON**","Constitution", True if persona.FAMILY == "Robot" else False),
                ("**DEX**","Dexterity",True if persona.FAMILY == "Robot" else False),
                ("**INT**","Intelligence",True if persona.FAMILY == "Robot" else False),
                ("**MSTR**","Mind",False),
                ("**PSTR**","Strength",True if persona.FAMILY == "Robot" else False),
                ("**SOC**","Privilege",False),
                ("**HPM**","Max Hit Points",False),
        ]

        self.set_xy(x+8,y+11)

        ### acronym line
        start_x = 18
        right_bump = 0 # total bump along x-axis
        bumpit = 22 # bump along x-axis increment

        self.set_font(family="helvetica",size=14)
        self.set_text_color(0) # black
        for attuple in attribute_formatting:
            acronym = attuple[0]
            self.set_x(start_x + right_bump)
            right_bump += bumpit #bump the next element right 
            self.cell(txt=acronym, align='X', markdown=True)

        ### value line
        ### uses stripped acronym to get data from record
        self.set_y(self.get_y()+8) 
        right_bump = 0
        self.set_font(family="helvetica",size=16)
        self.set_text_color(0) # black

        for attuple in attribute_formatting:
            acronym = attuple[0]
            acronym = acronym.strip("*")
            self.set_x(start_x + right_bump)
            right_bump += bumpit #bump the next attribute element right 
            blob = str(getattr(persona, acronym))

            # check for robotic primes
            if attuple[2]: # boolean if is a prime
                prime = acronym + '_PRIME'
                prime_add = int(getattr(persona,prime))
                blob += f'({prime_add})'
            self.cell(txt=blob, align='X', markdown=True)

        ### long version line
        self.set_y(self.get_y()+8)
        right_bump = 0
        self.set_font(family="helvetica",size=9)
        self.set_text_color(0) # black
        for attuple in attribute_formatting:
            long_name = attuple[1]
            self.set_x(start_x + right_bump)
            right_bump += bumpit #bump the next attribute element right 
            self.cell(txt=long_name, align='X', markdown=True)
    

    def persona_level_info(self, persona, x:float = 0, y:float = 0) -> None:
        '''
        prints the persona's vocation and level and exps goal
        '''

        exps_next = list(table.vocation_exps_levels[persona.Vocation].keys())[
            persona.Level - 1
        ].stop  # pulls next exps goal from range based on level

        # build a blob to use
        vocation_info = f'{persona.Vocation}' if persona.FAMILY == "Anthro" else f'{persona.FAMILY}'
        exps_info = f' **Level** {persona.Level} **EXPS** ({persona.EXPS}/{exps_next})'
        blob = vocation_info + exps_info
        self.print_MD_string(blob,12,x,y)

    def pdf_attack_table(self, persona, x:float = 0, y:float = 0)->float:
        '''
        prints the attack table  makes a list for table_vomit
        A = Strike, B = Fling, C = Shoot
        BP = Skilled, BNP = Raw, MR = Max, DB = Force
        '''

        self.set_xy(x,y)
        attack_table = attack_table_composer(persona)

        data = [
            [
                "Type:LB",
                "Raw:CB",
                "Skilled:CB",
                "Max:CB",
                "Force:CB",
            ]
        ]

        # build data if BP exists.
        if attack_table["A"]["BP"] > 0:
            data.append(
                [
                    "Strike:LB",
                    f'{attack_table["A"]["BNP"]}:CI',
                    f'{attack_table["A"]["BP"]}:CI',
                    f'{attack_table["A"]["MR"]}:CI',
                    f'{attack_table["A"]["ADB"]}:CI',
                ]
            )

        if attack_table["B"]["BP"] > 0:
            data.append(
                [
                    "Fling:LB",
                    f'{attack_table["B"]["BNP"]}:CI',
                    f'{attack_table["B"]["BP"]}:CI',
                    f'{attack_table["B"]["MR"]}:CI',
                    f'{attack_table["B"]["BDB"]}:CI',
                ]
            )

        if attack_table["C"]["BP"] > 0:
            data.append(
                [
                    "Shoot:LB",
                    f'{attack_table["C"]["BNP"]}:CI',
                    f'{attack_table["C"]["BP"]}:CI',
                    f'{attack_table["C"]["MR"]}:CI',
                    f'{attack_table["C"]["CDB"]}:CI',
                ]
            )
 
        # table_vomit the ABCs of combat table
        self.table_vomit(data, 9, 105, self.get_y(), 1.5, 0.25)


    def combat_table_explainer(self, persona, x:float = 0, y:float = 0) -> float:
        '''
        prints an explainer and proficiency information
        '''
        attack_table = attack_table_composer(persona)
        y_bump = 5.4
        self.print_MD_string(f"**Raw:** Add to Unskilled Attack Rolls  **Skilled:** Add to Skilled Attack Rolls **Max:**  Maximum Attack Roll **Force:** Add to damage roll",10,x,y)
        y+=y_bump
        self.print_MD_string(f"**Strike:** fist, sword, club  **Fling:** bow, spear, spit **Shoot:** gun, lazer, fission **Sotto/Flotto:** = Shoot **Grenade:** = Fling, no Force",10,x,y)
        y+=y_bump
        if persona.Vocation in ["Alien","Robot"]:
            blob = f'**Skilled Attacks**: {attack_table["A"]["PROF"]}'
        elif persona.Vocation in ["Mercenary", "Nothing"]:
            blob = f'**Skilled Attacks**: {attack_table["A"]["PROF"]}'
        else:
            blob = f'**Skilled Attacks**: Strike - {attack_table["A"]["PROF"]}, Fling - {attack_table["B"]["PROF"]}, Shoot - {attack_table["C"]["PROF"]}.'

        self.print_MD_string(blob,10,x,y)
        y+=y_bump
        return y


    def grey_box_title(self,blob, x=0,y=0)->None:
        '''
        prints a formatted title for string
        '''
        self.set_xy(x,y)
        self.set_fill_color(200)
        self.set_draw_color(75)
        self.set_line_width(.2)
        self.set_font("Helvetica", style='B',size=14)
        line_height = self.font_size * 1.6
        line_width = self.get_string_width(blob, markdown=True) + 2 # + x is padding

        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )
    

    def print_MD_string(self, blob: str = 'where da blob', font_size: int = 12, x:float = 0, y:float = 0)-> None:
        self.set_font("Helvetica", "", font_size)
        self.set_draw_color(0)
        line_height = self.font_size * 1.6
        self.set_xy(x,y)

        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

    def center_grid(self, radius=25)-> None:
        '''
        draws a center circle and grid lines
        '''
        self.radius = radius
        self.set_draw_color(255, 0, 0)  # Set color to red.
        self.set_line_width(0.3)  # Set line width.

        # Draw a circle at the center of the page.
        self.circle(
            (self.epw / 2 - self.radius / 2),
            (self.eph / 2 - self.radius / 2),
            self.radius,
            "D",
        )

        # Draw a vertical line down the center of the page.
        self.line(self.epw / 2, 0, self.epw / 2, self.eph)

        # Draw a horizontal line across the center of the page.
        self.line(0, self.eph / 2, self.epw, self.eph / 2)

        self.set_draw_color(190)  # Set color to light grey .
        self.set_line_width(0.2)  # Set line width.

        #cover page horizontal lines
        for y in range(0,int(self.eph),10):
            self.line(0,y,self.epw,y)

        #cover page in vertical lines
        for x in range(0,int(self.epw),10):
            self.line(x,0,x,self.eph)

    def pdf_do_not_use(self)->None:
        '''
        draws a obfuscating pattern
        prints plea to not use this page
        '''

        self.set_draw_color(32) # dark lines
        self.set_line_width(.3)

        # x = epw = 216, y = eph = 280  
        # perimeter  TL= 5, 13, TR= (self.epw - 10),13 BL= 5,(self.eph - 20) BR= (self.epw - 10), (self.eph - 20)

        #bezier top left to right side 
        for y in range(13,int(self.eph-10),10):
            self.line(5,13,self.epw-5,y)

        #bezier top right to left side 
        for y in range(13,int(self.eph-5),10):
            self.line(self.epw-10,13,  5,y)

        #bezier middle
        for x in range(5,int(self.epw-5),10):
            self.line((self.epw-10)/2,13, x, self.eph-8)

        blob = "DO NOT USE"
        x=((self.epw/2)-(self.get_string_width(blob)/2))
        y=self.eph/2
        self.grey_box_title(blob,x,y)
        y+=12

        blob = f"Keep notes on attached sheets"
        x=((self.epw/2)-(self.get_string_width(blob)/2))
        self.grey_box_title(blob,x,y)


    def locutus(self)->None:
        """
        draws an target at x and y on page
        """
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.3)  # Set line width.

        # make a green circle around locutus
        self.set_draw_color(0, 255, 0) # green
        radius = 15
        self.circle(
            (x - radius / 2),
            (y - radius / 2),
            radius,
            "D",
        )

        centering = radius/2
        self.set_draw_color(0,0,255) # blue     
        self.line(x-centering,y-centering, x+centering, y+centering)
        self.line(x-centering,y+centering,x+centering,y-centering)

    def table_vomit(
        self,
        data: list,
        x_left: float,
        x_right: float,
        why: float,
        line_height: float,
        border: float,
    ) -> None:
        '''
        prints out the given list
        only used for attack table
        '''

        table_width = x_right - x_left
        line_height = self.font_size * line_height
        border_on = 1 if border > 0 else 0
        width = border

        self.set_draw_color(0, 0, 0)
        self.set_line_width(width)
        self.set_y(why)
        for row in data:
            col_width = table_width / (len(row) if len(row) > 0 else 1)
            self.set_x(x_left)
            for datum in row:
                content, styling = datum.split(":")
                alignment = styling[0]
                accenture = styling[1] if len(styling) > 1 and styling[1] != "N" else ""

                self.set_font(self.font_family, accenture, self.font_size_pt)
                self.multi_cell(
                    w=col_width,
                    h=line_height,
                    txt=content,
                    border=border_on,
                    max_line_height=self.font_size,
                    ln=3,
                    align=alignment,
                )
            self.ln()

    def task_info(self, persona,x:float=0,y:float=0)->float:
        '''
        prints task info for vocation, alien and robot
        '''
        y_bump = 5.4
        x_bump = 40
        task_title_top = y

        if persona.Vocation == "Alien":
            self.print_MD_string('**Alien Tasks** Find sustenance and reproduce.', 12, x,task_title_top)
            y+=y_bump
            return y
 
        if persona.Vocation == "Robot":
            self.print_MD_string('**Robot Tasks** Do what they are meant to do.', 12, x,task_title_top)
            y+=y_bump
            return y

        ### vocation GIFTS
        self.print_MD_string('**GIFTS**', 12, x,task_title_top)
        y+=y_bump
        gift_list = vocation.update_gifts(persona)
        for number,gift in enumerate(gift_list,1):
            self.print_MD_string(f"{number}) {gift}",12,x,y)
            y+=y_bump

        ### vocation INTERESTS
        x+=x_bump
        y=task_title_top
        self.print_MD_string('**INTERESTS**',12,x,y)
        y+=y_bump
        collated_interests = please.collate_this(persona.Interests)
        for number, interest in enumerate(collated_interests,1):
            self.print_MD_string(f"{number}) {interest}",12,x,y)
            y+=y_bump

        ### vocation  SKILLS
        ### skills are 3 column
        x+=x_bump
        y=task_title_top
        self.print_MD_string("**SKILLS**",12,x,y)
        y+=y_bump

        collated_skills = please.collate_this(persona.Skills)
        for number, skill in enumerate(collated_skills,1):
            if number == 4: #shift to row 2
                x+=x_bump 
                y=task_title_top + y_bump
            if number == 7: # shift to row 3
                x+=x_bump
                y=task_title_top + y_bump
            if number == 10: # shift to row 4
                x+=x_bump
                y=task_title_top + y_bump
            self.print_MD_string(f"{number}) {skill}",12,x,y)
            y+=y_bump

        line_amount = [len(gift_list), len(collated_interests),len(collated_skills)]
        one2three = max(line_amount)
        y = 3+task_title_top + y_bump*(3 if one2three > 2 else one2three)

        ### additional skill explainer
        x=8
        y+=3 
        blob = f'**Gifts:** Auto success. **Interests:** General knowledge (+1) **Skills:** Specific knowledge (+2)'
        if persona.Vocation == "Spie":
            blob = vocation.spie_martial_arts(persona)

        if persona.Vocation == "Nothing":
            if persona.EXPS > persona.Vocay_Aspiration_EXPS:
                achievation = "Achieved!"
            else:
                fraction = int((persona.EXPS / persona.Vocay_Aspiration_EXPS) * 100)
                achievation = f"{fraction}% achieved"
            blob = f"Aspiration: {persona.Vocay_Aspiration} Objective: {achievation}"
        self.print_MD_string(blob,10,x,y)
        y+= y_bump

        return y

    def mutation_to_pdf(self,persona,x:float=0,y:float=0)->float:
        '''
        prints mutation status and existing mutations 
        '''

        if persona.FAMILY == "Anthro":
            family_header = "Mutations:"
        elif persona.FAMILY == "Alien":
            family_header = "Powers:"
        elif persona.FAMILY == "Robot":
            family_header = "Malfunctations:"
        else:
            family_header = "Oops wrong family header"
        
        y_bump = 5.6

        if len(persona.Mutations) == 0:
            self.print_MD_string(f"**{family_header}** None", 12, x, y)
            y+=y_bump
            
        else:
            self.print_MD_string(f"**{family_header}**", 12, x, y)
            y+=y_bump            
            tiny_bump = 3.4

            all_mutations = mutations.mutation_list_builder()
            for mutation_name in sorted(persona.Mutations.keys()):
                mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)

                working_mutation = mutuple[1](persona)

                header, details, param = working_mutation.return_details(
                    working_mutation.__class__
                )
                self.print_MD_string(f"**{header}**",10,x,y)
                x+=4 + self.get_string_width(f"**{header}**",markdown=True)
                self.print_MD_string(f"{details}",8,x,y+.5)
                y+=tiny_bump
                x=8
                self.print_MD_string(f"{param}",8,x,y)
                y+=tiny_bump
        return y

    def anthro_biologic_info(self, persona,x:float=0,y:float=0)->float:
        '''
        prints anthro bio info (physical attributes and mutations)
        '''
        y_bump = 5.3

        self.grey_box_title('BIO INFO',5,y)

        ### heading bio data
        # x = 7 + self.get_string_width('BIO INFO')
        self.print_MD_string(f'{persona.FAMILY} {persona.FAMILY_TYPE} {persona.FAMILY_SUB if persona.FAMILY_SUB else " "}',12,(x+9+self.get_string_width('BIO INFO')),y+.5)
        y+= 3 + y_bump

        blob = f"**Family** {persona.FAMILY} **Type:** {persona.FAMILY_TYPE} **Sub Type:** {persona.FAMILY_SUB} **Age:** {persona.Age} years **Hite:** {persona.Hite} cms **Wate:** {persona.Wate} kgs"
        self.print_MD_string(blob,12,x,y)
        y+=y_bump

        # print out Mutations
        y = self.mutation_to_pdf(persona, 8,y)

        return y


    def alien_biologic_info(self, persona,x:float=0,y:float=0)->float:
        '''
        prints the alien xenologic info 
        '''
        y_bump = 5.3

        self.grey_box_title('XENO INFO',5,y)
        x = 8 + self.get_string_width('XENO INFO')
        self.print_MD_string(f'{persona.FAMILY} {persona.FAMILY_TYPE} {persona.FAMILY_SUB if persona.FAMILY_SUB else " "}',12,x,y+.5)
        y+= 3+y_bump
        x=8

        # specific person age hite and wate
        blob = f"**Specific Alien:** {persona.Persona_Name} **Age:** {persona.Age} {persona.Alien_Age_Suffix} old. **Hite:** {persona.Size} **Wate:** {persona.Wate} {persona.Wate_Suffix}."
        self.print_MD_string(blob,12,x,y)
        y+=y_bump

        ### assign the y for Description
        top_y = y
        x = 8
        x_bump = 90

        ### Build left column list
        left_column =['**Detailed Desc**']

        desc_parts = [
            f"Head: {persona.Head.split(' (')[0]}{persona.Head_Adorn}",
            f"Body: {persona.Body.split(' (')[0]}{persona.Body_Adorn}",
            f"Arms: {persona.Arms.split(' (')[0]}{persona.Arms_Adorn}",
            f"Legs: {persona.Legs.split(' (')[0]}",
        ]
        left_column.extend(desc_parts)

        ### adding xenobiology
        left_column.append('**Xenobiology**')

        ### adding list of Biology
        left_column.extend(persona.Biology)

        ### right column
        right_column = ["**Life Cycle**"]
        right_column.extend(persona.Life_Stages)
        right_column.append("**Society**")
        right_column.extend(persona.Society)

        print(f'alien biologic info {left_column = }')
        print()
        print(f'alien biologic info {right_column = }')
        
        for element in left_column:
            self.print_MD_string(element,11,x,y)
            y+=y_bump

        left_bottom = y #store bottom y
        y = top_y
        x += x_bump # move column

        for element in right_column:
            self.print_MD_string(element,11,x,y)
            y+=y_bump

        y = left_bottom if left_bottom>y else y
        x = 8

        ### mutations are called Abilities or Powers for aliens

        return y

    def note_lines(self, lines:int, x:float = 0, y:float =0)-> None:
        '''
        draws a chosen number of lines
        '''
        y_bump = 8

        self.grey_box_title('NOTES',5,y)
        y+= y_bump

        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)

        for more_y in range(int(y),int(y+y_bump*lines),8):
            self.line(8, more_y, 210, more_y)

    def equipment_lines(self, persona, lines:int, x:float = 0, y:float = 0)->float:
        '''
        prints weight allowance and equipment title lines
        draws split lines for equipment
        '''
        
        y_bump = 8
        self.grey_box_title('TOYS',5,y)
        x+= 3 + self.get_string_width("TOYS")
        self.print_MD_string(f"**Carry:** up to {persona.WA*1.5} kg = {persona.Move} h/u. **Sprint:** <{persona.WA/4} kg = {persona.Move*2} h/u. **Lift:** {persona.WA*2.5} kg = 0 h/u.",12,x,y)
        y+= 3 + y_bump

        ### item wate info header
        self.print_MD_string(f'**ITEM**{" "*48}**WT**{" "*7}**TTL**{" "*7}**INFO**',12,8,y)
        y+= y_bump*1.5

        # equipment lines to PDF
        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)

        for more_y in range(int(y),int(y+y_bump*lines),8):
            self.line(8, more_y, 69,more_y) # item
            self.line(73,more_y, 86,more_y) #wt
            self.line(90,more_y, 103,more_y) #ttl
            self.line(107,more_y, 208,more_y) #info
            
        return more_y
    
    def referee_persona_fun(self,persona,x:float=0,y:float=0)-> float:
        '''
        prints referee persona role playing suggestions
        '''
        y_bump = 5.6
        self.grey_box_title("ROLE PLAY FUN",x,y)
        y += 2+y_bump
        for fun in persona.RP_Fun:
            self.print_MD_string(fun,12,8,y)
            y += y_bump
        return y

    def trackers(self,x:float=0,y:float=0):
        y_bump = 8
        self.grey_box_title('TRACKERS',5,y)
        y+=y_bump*1.5
        self.set_xy(8,y)
        self.set_font('ZapfDingbats','',18)
        self.cell(txt=f'{"m"*5}  {"m"*5} {"m"*5}     {"m"*5}  {"m"*5} {"m"*5}', align='L')
        y += y_bump
        self.set_xy(8,y)
        self.cell(txt=f'{"o"*5}  {"o"*5} {"o"*5}  {"o"*5} {"o"*5}  {"o"*5} {"o"*5}', align='L')


##############################################
#
# functions to support outputs
#
##############################################


# fix broken pdf to browser 
def show_pdf(file_name: str = "37bf560f9d0916a5467d7909.pdf", search_path: str = "C:/") -> None:
    """
    finds the specified file on computer
    then shows it in the default browser
    """
    file_dos = r'C:\Users\mobil\Documents\EXP_Game_Tools\Records\Bin\37bf560f9d0916a5467d7909.pdf'

    try:
        for root, _, files in os.walk(search_path):
            if file_name in files:
                found_file = os.path.join(root, file_name)
                browser_file = "file:///" + found_file.replace('\\','/')
                print(f'{file_name = } {browser_file = }')
                webbrowser.get('windows-default').open_new('file:///C:/Users/mobil/Documents/EXP_Game_Tools/Records/Bin/37bf560f9d0916a5467d7909.pdf')
                #webbrowser.get('brave').open_new(browser_file)
                #webbrowser.open_new(browser_file)
                #webbrowser.open(browser_file)
                break
    except PermissionError:
        print(f"Permission denied for directory {root}. Continuing search...")
    except Exception as e:
        print(f"An error occurred: {e}")

def attack_table_composer(attack_tabler:table.PersonaRecord)-> dict:
    '''
    creates an attack table dictionary based on FAMILY 
    '''
    # collect core needed data
    awe = attack_tabler.AWE
    dex = attack_tabler.DEX
    intel = attack_tabler.INT
    pstr = attack_tabler.PSTR
    family = attack_tabler.FAMILY
    vocation = attack_tabler.Vocation
    level = attack_tabler.Level
    table_level = (
        attack_tabler.Level - 1 if attack_tabler.Level < 11 else 9
    )  # no level bonus for level one

    ### define the empty combat dictionary
    attack_table = {
        "A": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "B": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "C": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        #"TITLE": f"{vocation} LVL {level}",
        #"ARMOVE": f"Armour Rating (AR): {calc.AR}      Move: {calc.Move} h/u",
    }

    ### determine which attack table info is applicable
    if vocation not in ["Alien","Robot"]: 
        # Vocation STRIKE row (Type A)
        ABP = math.ceil((1.5 * awe) + (2 * dex) + (1.5 * intel) + (5 * pstr))
        ABP = ABP + table.vocation_level_bonus[vocation]["A"] * level
        ABNP = math.ceil(ABP * table.vocation_non_proficient[vocation]["A"] / 100)
        AMR = 625 + ABP
        ADB = math.ceil(pstr / 2)
        APROF = table.vocation_proficiencies[vocation]["A"][table_level]

        # Vocation FLING row (Type B)
        BBP = awe + (4 * dex) + intel + (2 * pstr)
        BBP = BBP + table.vocation_level_bonus[vocation]["B"] * level
        BBNP = math.ceil(BBP * (table.vocation_non_proficient[vocation]["B"] / 100))
        BMR = 650 + BBP
        BDB = math.ceil(pstr / 4)
        BPROF = table.vocation_proficiencies[vocation]["B"][table_level]

        # Vocation SHOOT row (Type C)
        CBP = awe + (9 * dex) + intel + pstr
        CBP = CBP + table.vocation_level_bonus[vocation]["C"] * level
        CBNP = math.ceil(CBP * (table.vocation_non_proficient[vocation]["C"] / 100))
        CMR = 675 + CBP
        CDB = 0
        CPROF = table.vocation_proficiencies[vocation]["C"][table_level]

        # Vocation PROF assignment
        if APROF == 42 and vocation == "Mercenary":
            APROF = BPROF = CPROF = "All weapons."

        elif APROF == 42 and vocation == "Nothing":
            APROF = BPROF = CPROF = "There can be only one."

    # todo calculate alien movement on the fly
    elif vocation == "Alien":
        # specific alien attributes
        attacks = attack_tabler.Attacks

        # Alien STRIKE row (Type A)
        if "Strike" in attacks:
            ABP = ABNP = 10 * (pstr + level)
            AMR = 700 + ABP
            ADB = level
        else:
            ABP = ABNP = AMR = ADB = 0

        # Alien FLING row (Type B)
        if "Fling" in attacks:
            BBP = BBNP = 10 * (dex + level)
            BMR = 700 + BBP
            BDB = level
        else:
            BBP = BBNP = BMR = BDB = 0

        # Alien SHOOT row (Type C)
        if "Shoot" in attacks:
            CBP = CBNP = 10 * (intel + level)
            CMR = 700 + CBP
            CDB = level
        else:
            CBP = CBNP = CMR = CDB = 0
        
        # populate the PROF column
        APROF = BPROF = CPROF = f"Natural."

    elif family == "Robot":
        # specific robot attributes
        pstr_prime = attack_tabler.PSTR_Prime
        dex_prime = attack_tabler.DEX_Prime
        intel_prime = attack_tabler.INT_Prime

        # Robot STRIKE row (Type A)
        ABP = (5 * dex) + (5 * intel) + (pstr_prime * pstr) + (level * pstr)
        ABNP = 0
        AMR = "---"
        ADB = pstr

        # Robot FLING row (Type B)
        BBP = (5 * awe) + (5 * pstr) + (dex_prime * dex) + (level * dex)
        BBNP = 0
        BMR = "---"
        BDB = math.ceil(pstr / 2)

        # Robot SHOOT row (Type C)
        CBP = (5 * awe) + (5 * dex) + (intel_prime * intel) + (level * intel)
        CBNP = 0
        CMR = "---"
        CDB = 0
        
        # populate the PROF column
        APROF = BPROF = CPROF = "Robots have no weapon skills."

    ### build the attack table to return
    # assign STRIKE row(ABP, ABNP, AMR, ADB)
    attack_table["A"]["BP"] = ABP
    attack_table["A"]["BNP"] = ABNP
    attack_table["A"]["MR"] = AMR
    attack_table["A"]["ADB"] = ADB

    # assign FLING row (BBP, BBNP, BNR, BDB)
    attack_table["B"]["BP"] = BBP
    attack_table["B"]["BNP"] = BBNP
    attack_table["B"]["MR"] = BMR
    attack_table["B"]["BDB"] = BDB

    # assign SHOOT row (CBP, CBNP, CMR, CDB)
    attack_table["C"]["BP"] = CBP
    attack_table["C"]["BNP"] = CBNP
    attack_table["C"]["MR"] = CMR
    attack_table["C"]["CDB"] = CDB

    # assign the Proficiency Column
    attack_table["A"]["PROF"] = APROF
    attack_table["B"]["PROF"] = BPROF
    attack_table["C"]["PROF"] = CPROF

    return attack_table


def screen_attack_table(persona) -> None:
    '''
    screen prints the attack table
    '''

    attack_table = attack_table_composer(persona)

    # prep the combat table
    ABP = attack_table["A"]["BP"]
    ABNP = attack_table["A"]["BNP"]
    AMR = attack_table["A"]["MR"]
    ADB = attack_table["A"]["ADB"]
    APROF = attack_table["A"]["PROF"]

    BBP = attack_table["B"]["BP"]
    BBNP = attack_table["B"]["BNP"]
    BMR = attack_table["B"]["MR"]
    BDB = attack_table["B"]["BDB"]
    BPROF = attack_table["B"]["PROF"]

    CBP = attack_table["C"]["BP"]
    CBNP = attack_table["C"]["BNP"]
    CMR = attack_table["C"]["MR"]
    CDB = attack_table["C"]["CDB"]
    CPROF = attack_table["C"]["PROF"]

    ### sort between different PROF types.
    # mercenary all profs
    # nothing blank, one weapon only, blank
    # all other vocations have an int
    # aliens evolved attacks only
    # robots baked in attacks only

    # manipulate the proficiency sentence for screen output

    '''    if str(BPROF) in ["All weapons.", "One single proficiency."]:
        # if mercenary or nothing
        pass
    elif str(APROF).split("-")[0] in ["Baked in attacks only.", "Natural "]:
        # if alien or robot
        pass
    else:
        # has int for PROF == Vocation
        for proficiency in ["APROF", "BPROF", "CPROF"]:
            nummer_profs = attack_table[proficiency[0]][proficiency[1:]]
            attack_table[proficiency[0]][
                proficiency[1:]
            ] = f"{table.numbers_2_words[int(nummer_profs)].capitalize()} {table.attack_type_words[proficiency]} weapons."
    '''

    # assign proficiencies 
    APROF = table.numbers_2_words[APROF] if isinstance(APROF,int) else APROF
    BPROF = table.numbers_2_words[APROF] if isinstance(APROF,int) else APROF
    CPROF = table.numbers_2_words[CPROF] if isinstance(CPROF,int) else CPROF

    # print out the combat table
    print(f'\nATTACK TABLE -- {persona.Vocation}')
    print(f'{" ":>6} {"BP":>5} {"BNP":>5} {"MR":>5} {"DB":>5} {"PROF":>5}')
    if ABP > 0:
        print(f"Type A {ABP:>5} {ABNP:>5} {AMR:>5} {ADB:>5}  {APROF}")
    if BBP > 0:
        print(f"Type B {BBP:>5} {BBNP:>5} {BMR:>5} {BDB:>5}  {BPROF}")
    if CBP > 0:
        print(f"Type C {CBP:>5} {CBNP:>5} {CMR:>5} {CDB:>5}  {CPROF}")

    if persona.FAMILY == 'Alien':
        blob = f'MOVE:  land {persona.Move_Land} h/u, air {persona.Move_Air} h/u, water {persona.Move_Water} h/u. ARMOUR RATING: {persona.AR}'      
    else:
        blob = f'MOVE:  {persona.Move} h/u  ARMOUR RATING: {persona.AR}'

    print(blob)    

    return



#####################################
#  PDF print outs
#####################################

def pdf_output_chooser(persona) -> None:
    '''
    choose between pdf styles
    '''
    function_map = {
        "One Shot - One sheet": pdf_one_shot,
        "Campaign - Two sheets": pdf_campaign,
    }
    choice_list = [key for key in function_map]
    function_chosen  = please.choose_this(choice_list, "PDF type needed? ")
    function_map[function_chosen](persona)
    
def pdf_campaign(persona) -> None:
    '''
    generates a campaign PDF 2 PAGES 4 sided
    allows for equipment and notes to be preserved between front_sheet updates 
    '''
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    ### PAGE ONE front
    persona_front_sheet(pdf,persona)

    ### PAGE ONE back
    pdf.add_page() # back page 1
    pdf.pdf_do_not_use() # here for lowest z
    pdf.title_line(persona,'Campaign')
    pdf.data_footer(persona)
    pdf.perimiter_box()

    ### PAGE TWO front
    pdf.add_page()
    pdf.title_line(persona,'Campaign')
    pdf.equipment_lines(persona, 28,8,16)
    pdf.data_footer(persona)
    pdf.perimiter_box()

    ### PAGE TWO back
    pdf.add_page()
    pdf.title_line(persona,'Campaign')
    pdf.note_lines(28,8,16)
    pdf.data_footer(persona)
    pdf.perimiter_box()

    
    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )
    show_pdf()

def pdf_one_shot(persona) -> None:
    '''
    generates a one_shot PDF 1 sheet 2 pages
    used for RPs or minimal note personas
    '''
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    persona_front_sheet(pdf, persona)
    equip_notes_one_shot(pdf,persona)

    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )
    show_pdf()

def persona_front_sheet(pdf, persona)->None:
    '''
    organizes print out of all persona data on one page
    '''
    pdf.set_margin(0)
    the_y = 18
    
    pdf.add_page()
    pdf.title_line(persona)
    pdf.data_footer(persona)

    ### attributes 3 line all calculated
    pdf.attributes_lines(persona,8,the_y)   

    ### combat heading
    the_y+=32
    pdf.grey_box_title('COMBAT INFO',5,the_y)

    ### combat info
    x=9 + pdf.get_string_width('COMBAT INFO')
    pdf.persona_level_info(persona,x,the_y+.5)
    
    ### building move, AR, line 
    x=8
    the_y+=8
    
    ### movement
    blob = '**MOVE**'

    if persona.FAMILY == 'Alien':
        blob += f'  land {persona.Move_Land} h/u, air {persona.Move_Air} h/u, water {persona.Move_Water} h/u.'      
    else:
        blob += f'  {persona.Move} h/u'

    pdf.print_MD_string(blob, 14,x,the_y)

    ### armour rating
    x+= 4 + pdf.get_string_width(blob)
    pdf.print_MD_string("**ARMOUR RATING (AR)**",14,x,the_y)
    x+= 1 + pdf.get_string_width("**ARMOUR RATING (AR)**", markdown=True)
    pdf.print_MD_string(f'{persona.AR}   **____   ____**',14,x,the_y)

    ### attack table header
    the_y+=8
    pdf.print_MD_string('**ATTACK TABLE**', 14,8,the_y)
    
    ### hit points header
    pdf.print_MD_string(f'**HIT POINTS (MAX = {persona.HPM})**', 14,105,the_y)

    ### proficiencies header
    pdf.print_MD_string('**Conditions**',14,162,the_y)

    ### hit points box
    the_y +=8
    pdf.set_line_width(.3)
    pdf.rect(106, the_y, 54, 29.6, "D")

    ### skilled weapon lines
    pdf.set_line_width(.2)
    pdf.set_draw_color(80)
    for y in range(the_y,the_y+36,6):
        pdf.line(162,y,208,y)

    ### combat table output
    # for now aliens only get vocation table if they have a vocation
    pdf.pdf_attack_table(persona,8,the_y)

    ### combat table explainer
    the_y += 30
    the_y = pdf.combat_table_explainer(persona,8,the_y)

    ### task info plus level info
    pdf.grey_box_title('TASK INFO',5,the_y)
    x = 9 + pdf.get_string_width('TASK INFO')
    pdf.persona_level_info(persona,x,the_y+.5)

    ### output multicolumn gifts, interests, skills
    the_y+=8
    the_y = 2+pdf.task_info(persona,8,the_y)

    ### bio (xeno and tech ) data
    if persona.FAMILY == 'Anthro':
        the_y = 3 + pdf.anthro_biologic_info(persona,8,the_y)
    elif persona.FAMILY == 'Alien':
        the_y = 3 + pdf.alien_biologic_info(persona,8,the_y)

    if persona.RP:
        pdf.referee_persona_fun(persona,5,the_y)
        the_y+=32

    if persona.RP and persona.FAMILY == "Alien":
        pdf.referee_combat_block(persona)

    if the_y < 250:
        pdf.trackers(8,the_y)

    pdf.perimiter_box() #placed here for z cover

def equip_notes_one_shot(pdf, persona)->None:
    '''
    full page of equip and notes for one shot
    '''

    # todo should aliens NOT have equipment if feral?
    pdf.add_page()
    pdf.title_line(persona)
    the_y = pdf.equipment_lines(persona, 14,8,16)
    the_y += 3
    pdf.note_lines(13,5,the_y)
    pdf.data_footer(persona)
    pdf.perimiter_box()

#####################################
# ALIEN output to screen
#####################################

def alien_screen(screenery:table.PersonaRecord) -> None:
    """
    screen prints alien persona
    """

    # clearance for Clarence
    please.clear_console()


    print(
        f"ALIEN PERSONA RECORD\n"
        f"Persona: {screenery.Persona_Name} \t\tPlayer Name: {screenery.Player_Name} \tCreated: {screenery.Date_Created}\n"
        f"AWE: {screenery.AWE} CHA: {screenery.CHA} CON: {screenery.CON} DEX: {screenery.DEX} "
        f"INT: {screenery.INT} MSTR: {screenery.MSTR} PSTR: {screenery.PSTR} HPS: {screenery.HPM} SOC: {screenery.SOC} WA: {screenery.WA}\n"
        f"Family: {screenery.FAMILY} Species: {screenery.FAMILY_TYPE}\n"
        f"Age: {screenery.Age} {screenery.Age_Suffix} Size: {screenery.Size_Cat} Wate: {screenery.Wate} {screenery.Wate_Suffix}"
    )


    if screenery.Vocation != "Alien":
        print(f"Vocation: {screenery.Vocation} Level: {screenery.Level} EXPS: {screenery.EXPS}")

    print("\nDESCRIPTION: " + screenery.Quick_Description)

    # four part description
    # the split removes the (l,a,w) movement info
    print(f"{screenery.Head.split(' (')[0]} head {screenery.Head_Adorn}")
    print(f"{screenery.Body.split(' (')[0]} body {screenery.Body_Adorn}")
    print(f"{screenery.Arms.split(' (')[0]} arms {screenery.Arms_Adorn}")
    print(f"{screenery.Legs.split(' (')[0]} legs")

    # show the combat table
    screen_attack_table(screenery)
    print(f'{screenery.Attack_Desc}')

    if screenery.Vocation != "Alien":
        # alien  Interest list
        screen_attack_table(screenery)
        print(f"\n{screenery.Vocation} GIFTS: ")
        gift_list = vocation.update_gifts(screenery)
        for x, gift in enumerate(gift_list):
            print(f"{x + 1}) {gift}")

        print(f"\n{screenery.Vocation} INTERESTS: ")
        collated_interests = please.collate_this(screenery.Interests)

        for x, interest in enumerate(collated_interests):
            print(f"{x + 1}) {interest}")

        # alien  Skills
        print(f"\n{screenery.Vocation} SKILLS: ")
        collated_skills = please.collate_this(screenery.Skills)
        for x, skill in enumerate(collated_skills):
            print(f"{x + 1}) {skill}")

    # print out the Alien powers aka mutations
    print(f"\nNATURAL POWERS of {screenery.FAMILY_TYPE}")

    if len(screenery.Mutations) == 0:
        print("None")


    else:
        all_mutations = mutations.mutation_list_builder()
        for mutation_name in screenery.Mutations.keys():
            mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)
            working_mutation = mutuple[1](screenery)
            working_mutation.post_details(working_mutation.__class__)

    print(f"\nBIOLOGY of {screenery.FAMILY_TYPE}")
    for bio_line in screenery.Biology:
        print(f"{bio_line}")
    print("")
    for stage,tuple_ in screenery.Life_Stages.items():
        print(f"{stage} {tuple_[0]} to {tuple_[1]} {screenery.Age_Suffix}")

    print(f"\nSOCIETY of {screenery.FAMILY_TYPE}")
    for soc_line in alien.society_output(screenery):
        print(f"{soc_line}")

    return None

#####################################
# ROBOT output to screen
#####################################

def robot_screen(bot_screen) -> None:
    """
    print the robot to screen
    """

    # clearance for Clarence
    ## please.clear_console()

    print("\n\n\nROBOT PERSONA RECORD")
    print(
        f"{bot_screen.Persona_Name} \t\tPlayer_Name: {bot_screen.Player_Name} \tDate: {bot_screen.Date_Created}\n"
        f"AWE: {bot_screen.AWE} CHA: {bot_screen.CHA} CON: {bot_screen.CON}({bot_screen.CON_Prime}) "
        f"DEX: {bot_screen.DEX}({bot_screen.DEX_Prime}) INT: {bot_screen.INT}({bot_screen.INT_Prime}) "
        f"MSTR: {bot_screen.MSTR} PSTR: {bot_screen.PSTR}({bot_screen.PSTR_Prime}) HPS: {bot_screen.HPM}\n"
        f"Adaptability: {bot_screen.Adapt}  Control Factor: {bot_screen.CF}  Fabricator: {bot_screen.Base_Family}\n"
        f"Family: {bot_screen.FAMILY} Type: {bot_screen.Bot_Type} Sub-Type: {bot_screen.Sub_Type} Model: {bot_screen.Robot_Model}\n"
    )

    print("APPEARANCE")
    print(f"{bot_screen.Description} \nWate: {bot_screen.Wate} kgs Hite: {bot_screen.Hite} cms")

    print("\nMECHANICS")
    print(
        f"Power Plant: {bot_screen.Power_Plant} Power Reserve: {bot_screen.Power_Reserve} months\n"
    )
    print(f"Sensors: {bot_screen.Sensors}")
    print(f"Locomotion: {bot_screen.Locomotion}")

    print("\nATTACK Functions: ", end="")
    if len(bot_screen.Attacks) == 0:
        print("None")
    else:
        print("")
        for x, attack in enumerate(bot_screen.Attacks):
            print(f"{x + 1}) {attack}")

    print("\nDEFENCE Functions: ", end="")
    if len(bot_screen.Defences) == 0:
        print("None")
    else:
        print("")
        for x, defence in enumerate(bot_screen.Defences):
            print(f"{x + 1}) {defence}")

    print("\nPERIPHERAL Functions: ", end="")
    if len(bot_screen.Peripherals) == 0:
        print("None")
    else:
        print("")
        for x, periph in enumerate(bot_screen.Peripherals):
            print(f"{x + 1}) {periph}")

    print(f"\n{bot_screen.Bot_Type.upper()} ROBOT Spec Sheet: ", end="")
    if len(bot_screen.Spec_Sheet) == 0:
        print("None")
    else:
        print("")
        for x, periph in enumerate(bot_screen.Spec_Sheet):
            print(f"{x + 1}) {periph}")

    # show the combat table
    screen_attack_table(robot)

    if bot_screen.Vocation != "Robot":
        print("\nRobots do not get a VOCATION COMBAT TABLE. Sorry.\n")
        # robot vocation Gifts
        gift_list = vocation.update_gifts(robot)
        print(f"\n{bot_screen.Vocation} GIFTS: ")
        for x, gift in enumerate(gift_list):
            print(f"{x + 1}) {gift}")

        # robot vocation  Interest list

        print(f"\n{bot_screen.Vocation} INTERESTS: ")
        collated_interests = please.collate_this(bot_screen.Interests)

        for x, interest in enumerate(collated_interests):
            print(f"{x + 1}) {interest}")

        # robot vocation  Skills
        print(f"\n{bot_screen.Vocation} SKILLS: ")
        collated_skills = please.collate_this(bot_screen.Skills)
        for x, skill in enumerate(collated_skills):
            print(f"{x + 1}) {skill}")

#####################################
# ANTHRO output to screen
#####################################

def anthro_screen(persona) -> None:
    '''
    screen prints an anthro
    '''

    please.clear_console()
    print(
        f"\n\nANTHRO PERSONA RECORD\n"
        f"Persona: {persona.Persona_Name} \t\t\tPlayer: {persona.Player_Name} \tCreated: {persona.Date_Created}\n"
        f"AWE: {persona.AWE} CHA: {persona.CHA} CON: {persona.CON} DEX: {persona.DEX} "
        f"INT: {persona.INT} MSTR: {persona.MSTR} PSTR: {persona.PSTR} HPS: {persona.HPM} SOC: {persona.SOC} WA: {persona.WA}\n"
        f"Family: {persona.FAMILY} Type: {persona.FAMILY_TYPE} SubType: {persona.FAMILY_SUB}\n"
        f"Age: {persona.Age} years Hite: {persona.Hite} cms Wate: {persona.Wate} kgs\n"
        f"Vocation: {persona.Vocation} Level: {persona.Level} EXPS: {persona.EXPS}"
    )

    # show the combat table
    screen_attack_table(persona)

    # anthro Gifts
    gift_list = vocation.update_gifts(persona)
    print(f"\n{persona.Vocation} GIFTS: ")
    for x, gift in enumerate(gift_list):
        print(f"{x + 1}) {gift}")

    # anthro  Interest list
    print(f"\n{persona.Vocation} INTERESTS: ")
    collated_interests = please.collate_this(persona.Interests)

    for x, interest in enumerate(collated_interests, 1):
        print(f"{x}) {interest}")

    # anthro  Skills
    print(f"\n{persona.Vocation} SKILLS: ")
    collated_skills = please.collate_this(persona.Skills)
    for x, skill in enumerate(collated_skills, 1):
        print(f"{x}) {skill}")

    # special cases for nothing and spie

    if persona.Vocation == "Spie":
        print(f"{vocation.spie_martial_arts(persona)}")

    if persona.Vocation == "Nothing":
        if persona.EXPS > persona.Vocay_Aspiration_EXPS:
            achievation = "Achieved!"
        else:
            fraction = int((persona.EXPS / persona.Vocay_Aspiration_EXPS) * 100)
            achievation = f"{fraction}% achieved"

        print(f"Aspiration: {persona.Vocay_Aspiration} Objective: {achievation}")

    # print out Mutations
    print("\nMUTATIONS", end=" ")

    if len(persona.Mutations) == 0:
        print("None")

    else:
        all_mutations = mutations.mutation_list_builder()
        for mutation_name in persona.Mutations.keys():
            mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)
            working_mutation = mutuple[1](persona)
            working_mutation.post_details(working_mutation.__class__)

    if persona.RP:
        print("\nReferee Persona ROLE-PLAYING CUES")
        for fun in persona.RP_Fun:
            print(f"{fun}")

