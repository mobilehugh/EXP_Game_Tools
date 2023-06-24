import math
import os
import time
import webbrowser

from fpdf import FPDF

import please
import mutations
import vocation
import table

def outputs_workflow(persona, out_type: str) -> None:
    '''
    simplify output calls  by directing TYPE and needs
    '''

    family_type = persona.FAMILY

    if family_type == "Anthro" and out_type == "screen":
        anthro_screen(persona)  
    elif family_type in ["Anthro","Alien"] and out_type == "pdf":
        anthro_pdf_chooser(persona)
    elif family_type == "Alien" and out_type == "screen":
        alien_screen(persona)
    elif family_type == "Robot" and out_type == "screen":
        robot_screen(persona)
    elif family_type == "Robot" and out_type == "pdf":
        robot_pdf_creator(persona)
    elif family_type == "Toy" and out_type == "screen":
        print("this doesn't exist yet")
    elif family_type == "Toy" and out_type == "pdf":
        print("this doesn't exist yet")
    return

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

    def perimiter_box(self):
        # The rectangle's top left corner is at coordinates (5, 13).
        # subtracting 10 and 20 respectively to account for margins.
        # The 'D' argument indicates that the rectangle should be drawn (not filled).

        self.set_draw_color(0, 0, 0) 
        self.set_line_width(1)
        self.rect(5, 13, (self.epw - 10), (self.eph - 20), "D")

    def title_line(self, persona, title_name: str = 'PERSONA') -> None:
        # outputs a bespoke title at top of page. 
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

    def description_line(self, persona,x:float = 0, y:float=0):

        if persona.FAMILY == "Anthro":
            blob = f"{persona.Persona_Name} is a {persona.Age} year-old {persona.FAMILY_TYPE} {persona.FAMILY_SUB.lower()} {persona.Vocation.lower()}."
        elif persona.FAMILY == "Alien":
            blob = f"{persona.Persona_Name} is a {persona.Quick_Description}"
        elif persona.FAMILY == "Robot":
            blob = f"{persona.Persona_Name} is a {persona.Description}"
        else:
            blob = "ERROR: No description for this persona"

        self.print_MD_string(blob,14,x,y)

    def attributes_lines(self, persona, x:float=0,y:float=0)->None:
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
            if persona.FAMILY == "Robot":
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
    

    def persona_level_info(self, persona, x:float = 0, y:float = 0):

        exps_next = list(table.vocation_exps_levels[persona.Vocation].keys())[
            persona.Level - 1
        ].stop  # pulls next exps goal from range based on level

        # build a blob to use
        vocation_info = f'{persona.Vocation}' if persona.FAMILY == "Anthro" else f'{persona.FAMILY}'
        exps_info = f' **Level** {persona.Level} **EXPS** ({persona.EXPS}/{exps_next})'
        blob = vocation_info + exps_info
        self.print_MD_string(blob,12,x,y)

    def combat_table_pd_effer(self, persona, x:float = 0, y:float = 0):
        '''
        organizes the table does a pdf output using table_vomit
        A = Strike, B = Fling, C = Shoot
        BP = Skilled, BNP = Raw, MR = Max, DB = Force
        '''
        self.set_xy(x,y)
        attack_table = universal_combat_tabler(persona)

        print(please.show_me_your_dict(attack_table))
        print()
        input("safe to continue? ")


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
 
        print(data)
        print()
        input("safe to continue? ")

        # table_vomit the ABCs of combat table
        self.table_vomit(data, 9, 105, self.get_y(), 1.5, 0.25)


    def combat_table_explainer(self, x:float = 0, y:float = 0):
        self.print_MD_string(f"**Raw:** Add to Unskilled Attack Rolls  **Skilled:** Add to Skilled Attack Rolls **Max:**  Maximum Attack Roll **Force:** Add to damage roll",10,x,y)
        self.print_MD_string(f"**Strike:** fist, sword, club  **Fling:** bow, spear, spit **Shoot:** gun, lazer, fission **Sotto/Flotto:** = Shoot **Grenade:** = Fling, no Force",10,x,y+5.4)


    def alien_move(self, persona):
        move_type = ["Move_Land", "Move_Air", "Move_Water"]
        blob = ""

        for terrain in move_type:
            move_rate = getattr(persona, terrain)
            if move_rate > 0:
                blob += f'**{terrain.replace("_", " ")}:** {move_rate} h/u '

        self.set_font("Helvetica", size=12)
        line_height = self.font_size * 1.5
        self.set_xy(8, self.get_y())

        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
        )
 
    def grey_box_title(self,blob, x=0,y=0)->None:
        '''
        takes the blob string and makes it a box for it
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

    def liner_up(self, radius=100)-> None:
        '''
        places a circle around the center of the page and two lines
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

    def obfuscate(self)->None:
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


    def locutus(self):
        """
        makes an target at x and y
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
                print(f'in table_vomit {datum = }')
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

    def task_info(self, persona,x:float=0,y:float=0):
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
            blob = f"{persona.Spie_Fu}"

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

    def mutation_to_pdf(self,persona,x:float=0,y:float=0)->None:
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
            all_mutations = mutations.list_all_mutations()
            tiny_bump = 3.4
            for name in sorted(persona.Mutations.keys()):
                working_mutation = all_mutations[name](persona)
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

    def anthro_biologic_info(self, persona,x:float=0,y:float=0)->None:
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

    def referee_persona_fun(self,persona,x:float=0,y:float=0)-> None:
        y_bump = 5.6
        self.grey_box_title("ROLE PLAY FUN",x,y)
        y += 2+y_bump
        for fun in persona.RP_Fun:
            self.print_MD_string(fun,12,8,y)
            y += y_bump

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

    def alien_biologic_info(self, persona,x:float=0,y:float=0)->float:
        y_bump = 5.3

        self.grey_box_title('XENO INFO',5,y)
        x = 8 + self.get_string_width('XENO INFO')
        self.print_MD_string(f'{persona.FAMILY} {persona.FAMILY_TYPE} {persona.FAMILY_SUB if persona.FAMILY_SUB else " "}',12,x,y+.5)
        y+= y_bump

        # specific person age hite and wate
        blob = f"**Specific Alien:** {self.persona.Persona_Name} **Age:** {self.persona.Age} {self.persona.Alien_Age_Suffix} old. **Hite:** {self.persona.Size} **Wate:** {self.persona.Wate} {self.persona.Wate_Suffix}."
        self.print_MD_string(blob,12,x,y)
        y+=y_bump

        ### assign the y for Description
        top_y = y
        x = 8
        x_bump = 90

        ### Build left column list
        left_column =['**Detailed Desc']

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
        left_column.append(persona.Biology)

        ### right column
        right_column = ["**Life Cycle**"]
        right_column.extend(persona.Life_Cycle)
        right_column.append("**Society**")
        right_column.extend(persona.Society)

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
        y_bump = 8

        self.grey_box_title('NOTES',5,y)
        y+= y_bump

        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)

        for more_y in range(int(y),int(y+y_bump*lines),8):
            self.line(8, more_y, 210, more_y)

    def equipment_lines(self, persona, lines:int, x:float = 0, y:float = 0):
        ### wate allowance to PDF
        y_bump = 8
        self.grey_box_title('TOYS',5,y)
        x+= 3 + self.get_string_width("TOYS")
        self.print_MD_string(f"**Carry:** up to {persona.WA*1.5} kg = {persona.MOVE} h/u. **Sprint:** <{persona.WA/4} kg = {persona.MOVE*2} h/u. **Lift:** {persona.WA*2.5} kg = 0 h/u.",12,x,y)
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

##############################################
#
# functions to support outputs
#
##############################################

def show_pdf(file_name: str = "37bf560f9d0916a5467d7909.pdf", search_path: str = "C:/") -> None:
    """
    finds the specified file on computer
    then shows it in the default browser
    """
    try:
        for root, _, files in os.walk(search_path):
            if file_name in files:
                found_file = os.path.join(root, file_name)
                browser_file = "file:///" + found_file.replace('\\','/')
                webbrowser.get('windows-default').open_new(browser_file)
                break
    except PermissionError:
        print(f"Permission denied for directory {root}. Continuing search...")
    except Exception as e:
        print(f"An error occurred: {e}")

def universal_combat_tabler(persona)->dict:
    '''
    creates an attack table based on FAMILY 
    '''
    # collect core needed data
    awe = persona.AWE
    dex = persona.DEX
    intel = persona.INT
    pstr = persona.PSTR
    family = persona.FAMILY
    vocation = persona.Vocation
    level = persona.Level
    table_level = (
        persona.Level - 1 if persona.Level < 11 else 9
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

    elif vocation == "Alien":
        # specific alien attributes
        attacks = persona.Attacks
        per_unit = persona.Attack_Desc
        damage = f"{persona.Damage}"

        # Alien STRIKE row (Type A)
        ABP = ABNP = 10 * (pstr + level)
        AMR = 700 + ABP
        ADB = level

        # Alien FLING row (Type B)
        BBP = BBNP = 10 * (dex + level)
        BMR = 700 + BBP
        BDB = level

        # Alien SHOOT row (Type C)
        CBP = CBNP = 10 * (intel + level)
        CMR = 700 + CBP
        CDB = 0
        
        # populate the PROF column
        APROF = BPROF = CPROF = f"Natural - {attacks} {per_unit} for {damage} HPS."

    elif family == "Robot":
        # specific robot attributes
        pstr_prime = persona.PSTR_Prime
        dex_prime = persona.DEX_Prime
        intel_prime = persona.INT_Prime

        # Alien STRIKE row (Type A)
        ABP = (5 * dex) + (5 * intel) + (pstr_prime * pstr) + (level * pstr)
        ABNP = 0
        AMR = "---"
        ADB = pstr

        # Alien FLING row (Type B)
        BBP = (5 * awe) + (5 * pstr) + (dex_prime * dex) + (level * dex)
        BBNP = 0
        BMR = "---"
        BDB = math.ceil(pstr / 2)

        # Alien SHOOT row (Type C)
        CBP = (5 * awe) + (5 * dex) + (intel_prime * intel) + (level * intel)
        CBNP = 0
        CMR = "---"
        CDB = 0
        
        # populate the PROF column
        APROF = BPROF = CPROF = "None"

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


def output_combat_tabler(persona, combat_table):
    # prep the combat table
    ABP = combat_table["A"]["BP"]
    ABNP = combat_table["A"]["BNP"]
    AMR = combat_table["A"]["MR"]
    ADB = combat_table["A"]["ADB"]
    APROF = combat_table["A"]["PROF"]

    BBP = combat_table["B"]["BP"]
    BBNP = combat_table["B"]["BNP"]
    BMR = combat_table["B"]["MR"]
    BDB = combat_table["B"]["BDB"]
    BPROF = combat_table["B"]["PROF"]

    CBP = combat_table["C"]["BP"]
    CBNP = combat_table["C"]["BNP"]
    CMR = combat_table["C"]["MR"]
    CDB = combat_table["C"]["CDB"]
    CPROF = combat_table["C"]["PROF"]

    ### sort between different PROF types.
    # mercenary all profs
    # nothing blank, one weapon only, blank
    # all other vocations have an int
    # aliens evolved attacks only
    # robots baked in attacks only

    # manipulate the proficiency sentence for screen output

    if str(BPROF) in ["All weapons.", "One single proficiency."]:
        # if mercenary or nothing
        pass
    elif str(APROF).split("-")[0] in ["Baked in attacks only.", "Natural "]:
        # if alien or robot
        pass
    else:
        # has int for PROF == Vocation
        for proficiency in ["APROF", "BPROF", "CPROF"]:
            nummer_profs = combat_table[proficiency[0]][proficiency[1:]]
            combat_table[proficiency[0]][
                proficiency[1:]
            ] = f"{table.numbers_2_words[nummer_profs].capitalize()} {table.attack_type_words[proficiency]} weapons."

    # print out the combat table
    print(f'\nCOMBAT TABLE -- {combat_table["TITLE"]}')
    print(f'{" ":>6} {"BP":>5} {"BNP":>5} {"MR":>5} {"DB":>5} {"PROF":>5}')
    if ABP > 0:
        print(f"Type A {ABP:>5} {ABNP:>5} {AMR:>5} {ADB:>5}  {APROF}")
    if BBP > 0:
        print(f"Type B {BBP:>5} {BBNP:>5} {BMR:>5} {BDB:>5}  {BPROF}")
    if CBP > 0:
        print(f"Type C {CBP:>5} {CBNP:>5} {CMR:>5} {CDB:>5}  {CPROF}")

    if persona.FAMILY != "Alien":
        print(f'{combat_table["ARMOVE"]}')

    return

#####################################
# ANTHRO output to screen
#####################################

def anthro_screen(persona) -> None:
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
    vocation_combat_tabler(persona, "output")

    # anthro Gifts
    gift_list = vocation.update_gifts(persona)
    print(f"\n{persona.Vocation} GIFTS: ")
    for x, gift in enumerate(gift_list):
        print(f"{x + 1}) {gift}")

    # anthro  Interest list
    print(f"\n{persona.Vocation} INTERESTS: ")
    collated_interests = please.collate_this(persona.Interests)

    for x, interest in enumerate(collated_interests):
        print(f"{x + 1}) {interest}")

    # anthro  Skills
    print(f"\n{persona.Vocation} SKILLS: ")
    collated_skills = please.collate_this(persona.Skills)
    for x, skill in enumerate(collated_skills):
        print(f"{x + 1}) {skill}")

    # special cases for nothing and spie

    if persona.Vocation == "Spie":
        print(f"{persona.Spie_Fu}")

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
        all_mutations = mutations.list_all_mutations()

        for name, perm in sorted(persona.Mutations.items()):
            working_mutation = all_mutations[name](persona)
            working_mutation.post_details(working_mutation.__class__)

    if persona.RP:
        print("\nReferee Persona ROLE-PLAYING CUES")
        for fun in persona.RP_Fun:
            print(f"{fun}")

    return

#####################################
# ANTHRO output to PDF
#####################################

def anthro_pdf_chooser(persona) -> None:
    function_map = {
        "One Shot - One sheet": anthro_one_shot_creator,
        "Campaign - Two sheets": anthro_campaign_creator,
    }
    choice_list = [key for key in function_map]
    function_chosen  = please.choose_this(choice_list, "PDF type needed? ")
    function_map[function_chosen](persona)
    
def anthro_campaign_creator(persona) -> None:
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    ### PAGE ONE front
    persona_front_sheet(pdf,persona)

    ### PAGE ONE back
    pdf.add_page() # back page 1
    pdf.obfuscate() # here for lowest z
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

def anthro_one_shot_creator(persona) -> None:
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))

    persona_front_sheet(pdf, persona)
    do_not_use_back_sheet(pdf,persona)

    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )
    show_pdf()

def persona_front_sheet(pdf, persona):
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
    x+= 3+ pdf.get_string_width("**ARMOUR RATING (AR)**", markdown=True)
    pdf.print_MD_string(f'{persona.AR}   **_____   _____**',14,x,the_y)

    ### attack table header
    the_y+=8
    pdf.print_MD_string('**ATTACK TABLE**', 14,8,the_y)
    
    ### hit points header
    pdf.print_MD_string(f'**HIT POINTS (MAX = {persona.HPM})**', 14,105,the_y)

    ### proficiencies header
    pdf.print_MD_string('**Skilled Attacks**',14,162,the_y)

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
    pdf.combat_table_pd_effer(persona,8,the_y)

    ### combat table explainer
    the_y += 30
    pdf.combat_table_explainer(8,the_y+.5)

    ### task info plus level info
    the_y+=14
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

    if the_y < 250:
        pdf.trackers(8,the_y)

    pdf.perimiter_box() #placed here for z cover

    ##################################################
    # back page one off anthro
    #################################################

def do_not_use_back_sheet(pdf, persona):
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

def alien_screen(alien):
    """
    print the alien to screen
    """

    # clearance for Clarence
    please.clear_console()
    print(
        f"ALIEN PERSONA RECORD\n"
        f"Persona: {alien.Persona_Name} \t\tPlayer Name: {alien.Player_Name} \tCreated: {alien.Date_Created}\n"
        f"AWE: {alien.AWE} CHA: {alien.CHA} CON: {alien.CON} DEX: {alien.DEX} "
        f"INT: {alien.INT} MSTR: {alien.MSTR} PSTR: {alien.PSTR} HPS: {alien.HPM} SOC: {alien.SOC} WA: {alien.WA}\n"
        f"Family: {alien.FAMILY} Species: {alien.FAMILY_TYPE}\n"
        f"Age: {alien.Age} {alien.Alien_Age_Suffix} Size: {alien.Size} Wate: {alien.Wate} {alien.Wate_Suffix}"
    )

    if alien.Vocation != "Alien":
        print(f"Vocation: {alien.Vocation} Level: {alien.Level} EXPS: {alien.EXPS}")

    print("\nDESCRIPTION: " + alien.Quick_Description)

    # four part description
    # the split removes the (l,a,w) movement info
    print(f"{alien.Head.split(' (')[0]} head{alien.Head_Adorn}")
    print(f"{alien.Body.split(' (')[0]} body{alien.Body_Adorn}")
    print(f"{alien.Arms.split(' (')[0]} arms{alien.Arms_Adorn}")
    print(f"{alien.Legs.split(' (')[0]} legs")

    """
    print(f"Head: {alien.Head.split(' (')[0]}{alien.Head_Adorn}")
    print(f"Trso: {alien.Body.split(' (')[0]}{alien.Body_Adorn}")
    print(f"Arms: {alien.Arms.split(' (')[0]}{alien.Arms_Adorn}")
    print(f"Legs: {alien.Legs.split(' (')[0]}")
    """

    # show the combat table
    alien_combat_tabler(alien, "output")

    print("\nCOMBAT MOVEMENT RATES")
    if alien.Move_Land > 0:
        print(f"LAND: {alien.Move_Land} h/u ", end="")
    if alien.Move_Air > 0:
        print(f"AIR: {alien.Move_Air} h/u ", end="")
    if alien.Move_Water > 0:
        print(f"WATER: {alien.Move_Water} h/u ")

    if alien.Vocation != "Alien":
        # alien  Interest list
        vocation_combat_tabler(alien, "output")
        print(f"\n{alien.Vocation} GIFTS: ")
        gift_list = vocation.update_gifts(alien)
        for x, gift in enumerate(gift_list):
            print(f"{x + 1}) {gift}")

        print(f"\n{alien.Vocation} INTERESTS: ")
        collated_interests = please.collate_this(alien.Interests)

        for x, interest in enumerate(collated_interests):
            print(f"{x + 1}) {interest}")

        # alien  Skills
        print(f"\n{alien.Vocation} SKILLS: ")
        collated_skills = please.collate_this(alien.Skills)
        for x, skill in enumerate(collated_skills):
            print(f"{x + 1}) {skill}")

    # print out the Alien powers aka mutations
    print(f"\nNATURAL POWERS of {alien.FAMILY_TYPE}")

    if len(alien.Mutations) == 0:
        print("None")

    else:
        all_mutations = mutations.list_all_mutations()

        for name, perm in sorted(alien.Mutations.items()):
            working_mutation = all_mutations[name](alien)
            working_mutation.post_details(working_mutation.__class__)

    print(f"\nBIOLOGY of {alien.FAMILY_TYPE}")
    for bio_line in alien.Biology:
        print(f"{bio_line}")
    print("")
    for bio_line in alien.Life_Cycle:
        print(f"{bio_line}")

    print(f"\nSOCIETY of {alien.FAMILY_TYPE}")
    for soc_line in alien.Society:
        print(f"{soc_line}")

    return

#####################################
# AlIEN output to PDF
#####################################

def alien_pdf_creator(alien) -> None:
    '''
    creates an alien pdf and then shows it on the browser
    pdfs are no longer stored
    '''
    

#####################################
# ROBOT output to screen
#####################################

def robot_screen(robot) -> None:
    """
    print the robot to screen
    """

    # clearance for Clarence
    ## please.clear_console()

    print("\n\n\nROBOT PERSONA RECORD")
    print(
        f"{robot.Persona_Name} \t\tPlayer_Name: {robot.Player_Name} \tDate: {robot.Date_Created}\n"
        f"AWE: {robot.AWE} CHA: {robot.CHA} CON: {robot.CON}({robot.CON_Prime}) "
        f"DEX: {robot.DEX}({robot.DEX_Prime}) INT: {robot.INT}({robot.INT_Prime}) "
        f"MSTR: {robot.MSTR} PSTR: {robot.PSTR}({robot.PSTR_Prime}) HPS: {robot.HPM}\n"
        f"Adaptability: {robot.Adapt}  Control Factor: {robot.CF}  Fabricator: {robot.Base_Family}\n"
        f"Family: {robot.FAMILY} Type: {robot.Bot_Type} Sub-Type: {robot.Sub_Type} Model: {robot.Robot_Model}\n"
    )

    print("APPEARANCE")
    print(f"{robot.Description} \nWate: {robot.Wate} kgs Hite: {robot.Hite} cms")

    print("\nMECHANICS")
    print(
        f"Power Plant: {robot.Power_Plant} Power Reserve: {robot.Power_Reserve} months\n"
    )
    print(f"Sensors: {robot.Sensors}")
    print(f"Locomotion: {robot.Locomotion}")

    print("\nATTACK Functions: ", end="")
    if len(robot.Attacks) == 0:
        print("None")
    else:
        print("")
        for x, attack in enumerate(robot.Attacks):
            print(f"{x + 1}) {attack}")

    print("\nDEFENCE Functions: ", end="")
    if len(robot.Defences) == 0:
        print("None")
    else:
        print("")
        for x, defence in enumerate(robot.Defences):
            print(f"{x + 1}) {defence}")

    print("\nPERIPHERAL Functions: ", end="")
    if len(robot.Peripherals) == 0:
        print("None")
    else:
        print("")
        for x, periph in enumerate(robot.Peripherals):
            print(f"{x + 1}) {periph}")

    print(f"\n{robot.Bot_Type.upper()} ROBOT Spec Sheet: ", end="")
    if len(robot.Spec_Sheet) == 0:
        print("None")
    else:
        print("")
        for x, periph in enumerate(robot.Spec_Sheet):
            print(f"{x + 1}) {periph}")

    # show the combat table
    robot_combat_tabler(robot, "output")

    if robot.Vocation != "Robot":
        print("\nRobots do not get a VOCATION COMBAT TABLE. Sorry.\n")
        # robot vocation Gifts
        gift_list = vocation.update_gifts(robot)
        print(f"\n{robot.Vocation} GIFTS: ")
        for x, gift in enumerate(gift_list):
            print(f"{x + 1}) {gift}")

        # robot vocation  Interest list

        print(f"\n{robot.Vocation} INTERESTS: ")
        collated_interests = please.collate_this(robot.Interests)

        for x, interest in enumerate(collated_interests):
            print(f"{x + 1}) {interest}")

        # robot vocation  Skills
        print(f"\n{robot.Vocation} SKILLS: ")
        collated_skills = please.collate_this(robot.Skills)
        for x, skill in enumerate(collated_skills):
            print(f"{x + 1}) {skill}")

    return

#####################################
# ROBOT output to PDF
#####################################

def robot_pdf_creator(robot):
    '''
    creates a pdf for a robot 
    shows it in the browser PDFs are no longer stored
    '''
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    pdf.add_page()
    pdf.perimiter_box()
    pdf.title_line(robot)
    pdf.attributes_lines(robot)
    pdf.description_line(robot)
    if robot.Vocation != "Robot":
        pdf.persona_level_info(robot, "Vocation")
        pdf.combat_table_pd_effer(robot, "Vocation")
    pdf.persona_level_info(robot, "Robot")
    pdf.combat_table_pd_effer(robot, "Robot")
    if robot.Vocation != "Robot":
        pdf.task_info(robot)

    pdf.add_page()
    pdf.title_line(robot)
    pdf.perimiter_box()
    pdf.equipment_lines(robot)
    pdf.note_lines()
    pdf.data_footer(robot)

    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )
    show_pdf()


