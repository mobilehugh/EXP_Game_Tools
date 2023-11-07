import math
import os
import time
import webbrowser
import sys

from fpdf import FPDF
from dataclasses import dataclass
from typing import Tuple, Union

import alien
import please
import mutations
import vocation
import exp_tables

# todo RP combat block: weak strong cannon fodder, canon fodder and canonical
# todo proficiency slot with actual weapons

@dataclass 
class AllRecords(exp_tables.AllThings):
    pass

def outputs_workflow(outputter:AllRecords, out_type: str) -> None:
    '''
    divides outputs between screen and pdf
    '''
    out_type = "screen" if out_type not in ["pdf","screen"] else out_type

    if out_type == "pdf":
        pdf_output_chooser(outputter)

    elif out_type == "screen":
        please.screen_this(outputter)

    return None

################################################
#
# laws of fpdf
#
################################################
'''
US LETTER:  
width (x) 215.9 mm, height (y) = 279.4 mm
origin point = (0, 0) = Left, Top corner
x-coordinate increases moves right =  width = 215.9 = epw() = effective page width
y-coordinate increases moves down  = height = 279.4 = eph() = effective page height

UNITS:
numbers are  mm (millimeters) NOT pixels and are FLOATS
font size is in points 1/72 of an inch
on a 72 ppi screen a point = a pixel 
BUT 72 ppi screen is not guaranteed so must use millimeters

there are 25.4 mm in 1 inch
12 point font is 4.23 mm
arial 12 space = 1.8 mm 


WARNINGS:
1) set_y(y) resets x to 0 
must use set_xy(x,y) to work as expected

2) circle(x,y,radius)
to center a circle x,y represent the bounding box not x,y center of circle
self.circle(
    (x - radius / 2),
    (y - radius / 2),
    radius,
    "D",
        )

3) getting cross
Parameters for line: (x1, y1, x2, y2) where (x1, y1) is start point and (x2, y2) is end point
line(start_left,start_top, end_left, end_top)
line(50, 50, 70, 70)  # Line 1: from point (50, 50) to point (70, 70)
line(50, 70, 70, 50)  # Line 2: from point (50, 70) to point (70, 50)

4) fontery
font_size() changes width(x) and height(y) called line_height

TOOLS:
def convert_points_to_mm(font_size_points):
    inches = font_size_points / 72  # convert points to inches
    mm = inches * 25.4  # convert inches to mm
    return mm

locutus() # puts a target where xy is 
center_grid() # puts full page center target on a grid

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

# todo corrections for x axis (left to right) work using get_string_width, NOT line height

class PDF(FPDF):

    ## persona output functions 

    def persona_title(self, blob: str = 'where da blob', font_size: int = 12)-> None:
        '''prints PERSONA NAME above perimiter box left justified'''
        self.set_font("Helvetica", "", font_size)
        self.set_draw_color(0)
        line_height = self.font_size * 1.6

        self.cell(
            markdown=True,
            txt=blob,
        )

    def player_title(self, blob: str = 'where da blob', font_size: int = 12)-> None:
        '''prints PLAYER NAME above perimeter box right justified'''
        self.set_font("Helvetica", "", font_size)
        self.set_draw_color(0)
        line_height = self.font_size * 1.6
        left_push = self.get_string_width(blob)
        self.set_x(self.get_x()-left_push)

        self.cell(
            markdown=True,
            txt=blob,
            align="R",
            new_x="LMARGIN",
            new_y="NEXT"
        )

    def section_title(self, announce:str = "", drivel:str = "") -> None:
        '''
        prints a pre formatted section title and drivel
        '''

        # paint the swath
        self.set_fill_color(200)
        left, top, width, height = self.get_x(),self.get_y(),205,8
        self.rect(left,top,width,height, "F")

        self.set_draw_color(75)
        self.set_line_width(.4)
        self.set_font("Helvetica", style='B',size=14)
        line_height = 8
        announce_width = self.get_string_width(announce) + 2

        self.cell(
            announce_width,
            line_height,
            txt=announce,
            border=True,
            new_x="RIGHT",
            new_y="TOP"
        )

        self.set_font("Helvetica",size=14)
        self.set_xy(self.get_x() + 2, self.get_y() + 1.5)
        self.cell(
            txt=drivel,
        )

    def markdown(self, blob: str = 'where da blob',font_size: int = 14)-> None:
        '''
        a cell modified for markdown with default font_size
        '''

        self.set_font("Helvetica",size=font_size)
        line_height = self.font_size * 1.6
        line_width = self.get_string_width(blob, markdown=True) + 2

        self.cell(
            w=line_width,
            h=line_height,
            txt=blob,
            align="L",
            markdown=True,
            new_x="RIGHT",
            new_y="LAST",
        )

    def markdown_internal(self, blob: str = 'where da blob',font_size: int = 14)-> None:
        '''
        a cell modified for markdown with default font_size
        '''

        self.set_font("Helvetica",size=font_size)
        line_height = self.font_size * 1.6
        line_width = self.get_string_width(blob, markdown=True) + 2

        self.cell(
            w=line_width,
            h=line_height,
            txt=blob,
            align="L",
            markdown=True,
            new_x="LEFT",
            new_y="NEXT",
        )

    def attributes_table(self, persona:AllRecords) -> None:
        """
        prints atttribute acronyms, values (+/- primes) and descriptions (+/-)
        """
        TABLE_DATA = [
            ["AWE", "CHA", "CON", "DEX", "INT", "MSTR", "PSTR", "SOC", "HPM", ("Helvetica", "B", 14)],
            [persona.AWE, persona.CHA, persona.CON, persona.DEX, persona.INT, persona.MSTR, persona.PSTR, persona.SOC, persona.HPM,("Helvetica", "I",18)]
        ]
        if not persona.RP:
             TABLE_DATA.append(["Awareness", "Charisma", "Constitution", "Dexterity", "Intelligence", "Mind", "Strength", "Privilege", "Damagability", ("Helvetica","B", 7)])


        if persona.FAMILY == "Robot":
            prime_con = f'({persona.CON_Prime})'            
            prime_dex = f'({persona.DEX_Prime})'
            prime_int = f'({persona.INT_Prime})'
            prime_pstr = f'({persona.PSTR_Prime})'

            TABLE_DATA.append(["ROBOT", "PRIMES", prime_con, prime_dex, prime_int, "", prime_pstr, "", "",("Helvetica", "I",10)])

        col_width = 22.1
        row_height = 7
        start_right,top = self.set_or_get("top of attribute table")
        for data_row in TABLE_DATA:
            for datum in data_row[:-1]: # sliced to hide format tuple
                font,style,size = data_row[-1] # format tuple
                self.set_font(font,style=style,size=size)
                datum = str(datum) if isinstance(datum, int) else datum
                self.cell(
                    w=col_width, 
                    h=row_height, 
                    txt=datum, 
                    border=False, 
                    align='C',    
                    new_x="RIGHT",
                    new_y="LAST",
                    )
            top += row_height
            self.set_or_get(start_right,top,"new line")

    def persona_level_info(self, persona:AllRecords) -> str:
        '''
        returns the persona's vocation and level and exps goal
        '''
        exps_next = list(exp_tables.vocation_exps_levels[persona.Vocation].keys())[persona.Level][1]
        return f'{persona.Vocation} level {persona.Level}  EXPS {persona.EXPS}/{exps_next}'

    def persona_bio_info(self, persona:AllRecords) -> str:
        '''
        returns to persona's bio info
        '''
        bio_line = f"FAMILY: {persona.FAMILY} "
        bio_line += f"TYPE: {persona.FAMILY_TYPE} SUB: {persona.FAMILY_SUB}" if persona.FAMILY in ["Anthro", "Robot"] else f"SPECIES: {persona.FAMILY_SUB}"

        return bio_line

    def attack_table_pdf(self, persona:AllRecords)->None:
        '''
        attack table composition and print out combined
        A = Strike, B = Fling, C = Shoot
        BP = Skilled, BNP = Raw, MR = Max, DB = Force, PROF = Skills

        # assign STRIKE row(ABP, ABNP, AMR, ADB)
        attack_table["A"]["BP"] = ABP
        attack_table["A"]["BNP"] = ABNP
        attack_table["A"]["MR"] = AMR
        attack_table["A"]["ADB"] = ADB
        attack_table["A"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["A"][table_level]

        # assign FLING row (BBP, BBNP, BNR, BDB)
        attack_table["B"]["BP"] = BBP
        attack_table["B"]["BNP"] = BBNP
        attack_table["B"]["MR"] = BMR
        attack_table["B"]["BDB"] = BDB
        attack_table["B"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["B"][table_level]

        # assign SHOOT row (CBP, CBNP, CMR, CDB)
        attack_table["C"]["BP"] = CBP
        attack_table["C"]["BNP"] = CBNP
        attack_table["C"]["MR"] = CMR
        attack_table["C"]["CDB"] = CDB
        attack_table["C"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["C"][table_level]

        '''

        attack_table = attack_table_composer(persona)     

        # attack header line
        TABLE_DATA = (
            ("TYPE", "SKILLED", "RAW", "MAX", "FORCE", "Skills", f"Hit Points MAX = {persona.HPM}"),
            ("Strike", attack_table["A"]["BP"],attack_table["A"]["BNP"], attack_table["A"]["MR"], attack_table["A"]["ADB"], attack_table["A"]["PROF"],""),
            ("Fling", attack_table["B"]["BP"], attack_table["B"]["BNP"], attack_table["B"]["MR"], attack_table["B"]["BDB"], attack_table["B"]["PROF"],""),
            ("Shoot", attack_table["C"]["BP"],attack_table["C"]["BNP"], attack_table["C"]["MR"], attack_table["C"]["CDB"], attack_table["C"]["PROF"],"")
        )

        self.set_font("Helvetica", size=11)
        self.set_fill_color(255)
        with self.table(
            align="LEFT",
            width = 201,
            col_widths=(16, 20, 20, 20, 20, 66, 49),
            text_align=("LEFT", "CENTER", "CENTER", "CENTER", "CENTER", "LEFT","LEFT"),
            borders_layout="MINIMAL"
            ) as attack_table:
            for data_row in TABLE_DATA:
                row = attack_table.row()
                for datum in data_row:
                    row.cell(str(datum))

    def attack_table_explainer(self) -> None:
        '''
        prints out explainer of attack table
        '''
        blob = f"**Strike:** fist, sword, club  **Fling:** bow, spear, spit **Shoot:** gun, lazer, fission **Sotto/Flotto:** = Shoot **Grenade:** = Fling, no Force\n**Skilled:** Add to Skilled Attacks **Raw:** Add to Unskilled Attacks **Max:**  Highest Roll **Force:** Add to damage"
        self.set_font("Helvetica", size=10)
        self.multi_cell(0,5,txt= blob, markdown=True,new_x="LEFT",new_y="NEXT",)
        return

    def task_info(self, persona:AllRecords)->None:
        '''
        prints task info for vocation, alien and robot
        '''

        if persona.Vocation == "Alien":
            if persona.Society["Tools"] == "Flora or Fauna":
                self.markdown_internal('**Alien Tasks** Find sustenance and reproduce.', 12)
            else:
                self.markdown_internal(f'**Alien Tasks** Do what {persona.FAMILY_TYPE} are meant to do.', 12)
            return  # leave task info early
 
        if persona.Vocation == "Robot":
            self.markdown_internal(f'**Robot Tasks** Do what {persona.FAMILY_TYPE} bots are meant to do.', 12)
            return # leave task info early

        # if you are here you have a Vocation and Tasks
        # uses the multicolumn table trick

        ### GIFTS column
        gifts_column = ["GIFTS"]
        gifts_column.extend(vocation.update_gifts(persona))

        ### INTERESTS column
        interests_column = ["INTERESTS"]
        interests_column.extend(please.collate_this(persona.Interests))

        ### SKILLS column(s)

        skills_list = please.collate_this(persona.Skills)
        # how many columns of skills
        # change header to more skills
        skill_number = len(skills_list)
        if skill_number < 4:
            column_widths = (50, 50, 50)
            skills_one = ["SKILLS"] + skills_list
            zip_these = [gifts_column, interests_column, skills_one]
        elif skill_number < 7:
            column_widths = (50, 50, 50, 50)
            skills_one = ["SKILLS"] + skills_list[:3]
            skills_two = [" "] + skills_list[3:6] if skill_number >= 6 else [" "] + skills_list[3:]
            zip_these = [gifts_column, interests_column, skills_one, skills_two]
        elif skill_number < 10:
            column_widths = (40, 40, 40, 40, 40)
            skills_one = ["SKILLS"] + skills_list[:3]
            skills_two = [" "] + skills_list[3:6]
            skills_three = [" "] + skills_list[6:9] if skill_number >= 9 else [" "] + skills_list[6:]
            zip_these = [gifts_column, interests_column, skills_one, skills_two, skills_three]
        elif skill_number < 13:
            column_widths = (35, 35, 35, 35, 35, 35)
            skills_one = ["SKILLS"] + skills_list[:3]
            skills_two = [" "] + skills_list[3:6]
            skills_three = [' '] + skills_list[6:9]
            skills_four = [' '] + skills_list[9:12] if skill_number >= 12 else [" "] + skills_list[9:]
            zip_these = [gifts_column, interests_column, skills_one, skills_two, skills_three, skills_four]
        elif skill_number < 16:
            column_widths = (30, 30, 30, 30, 30, 30, 30)
            skills_one = ["SKILLS"] + skills_list[:3]
            skills_two = [" "] + skills_list[3:6]
            skills_three = [' '] + skills_list[6:9]
            skills_four = [' '] + skills_list[9:12]
            skills_five = [' '] + skills_list[12:15] if skill_number >= 15 else [" "] + skills_list[12:]
            zip_these = [gifts_column, interests_column, skills_one, skills_two, skills_three, skills_four,skills_five]
        elif skill_number < 19:
            column_widths = (25, 25, 25, 25, 25, 25, 25, 25)
            skills_one = ["SKILLS"] + skills_list[:3]
            skills_two = [" "] + skills_list[3:6]
            skills_three = [' '] + skills_list[6:9]
            skills_four = [' '] + skills_list[9:12]
            skills_five = [' '] + skills_list[12:15]
            skills_six = [' '] + skills_list[15:18] if skill_number >= 18 else [" "] + skills_list[15:]
            zip_these = [gifts_column, interests_column, skills_one, skills_two, skills_three, skills_four,skills_five, skills_six]

        else: 
            print(f'{skill_number} is too many damn skills. \nwrite them out your self')
            sys.exit()
        
        # column balancing
        max_len = len(max(zip_these, key=lambda x: len(x))) 
        min_len = len(min(zip_these, key=lambda x: len(x))) 
        delta = max_len - min_len

        for columns in [*zip_these]:
            if len(columns) < max_len:
                columns += " " * (delta)

        # create the thing
        TABLE_DATA = zip(*zip_these)

        # todo calculate the column widths based on longest line in each column
        self.set_font("Helvetica", size=10)
        self.set_fill_color(255)
        with self.table(
            align="LEFT",
            width = sum(column_widths),
            col_widths=column_widths,
            text_align="LEFT",
            borders_layout="NONE",
            line_height = 1.2 * self.font_size
            ) as attack_table:
            for data_row in TABLE_DATA:
                row = attack_table.row()
                for datum in data_row:
                    row.cell(str(datum))

        return

    def task_info_addendum(self, persona:AllRecords)-> None:
        '''task explainer plus nothing or spie stuff'''

        if persona.Vocation in ["Robot", "Alien"]:
            return # abort addendum if no vocation 

        # core explainer for tasks
        blob = f'**Gifts:** Specific task. Auto success. **Interests:** General knowledge (+1) **Skills:** Specific knowledge/task (+2)'

        # special addendum for spie and nothing
        if persona.Vocation == "Spie":
            blob += f"\n**Spie Fu**: {vocation.spie_martial_arts(persona)}"

        if persona.Vocation == "Nothing":
            exps, goal = persona.EXPS, persona.Vocay_Aspiration_EXPS
            achievation = "Completed!" if exps > goal else f"{int((exps / goal) * 100)}% achieved."
            blob += f"\nNothing aspiration: **{persona.Vocay_Aspiration}** Objective: {achievation}"

        self.set_font("Helvetica", size=10)
        self.multi_cell(0,5,txt= blob, markdown=True,new_x="LEFT",new_y="NEXT",)

        return

    def mutation_header(self, persona:AllRecords)->None:
        ''' 
        prints mutation status and existing mutations 
        '''

        pivot_mutation_name = {"Anthro":"**Mutations: ", "Alien":"**Evolutations: ", "Robot":"**Malfunctations: "}
        mutation_heading = pivot_mutation_name[persona.FAMILY]
        mutation_heading += "None**" if len(persona.Mutations) == 0 else "**"
        self.markdown_internal(mutation_heading, 12)
        return
        
    def mutation_list(self, persona:AllRecords):
        '''
        list the mutations, evolutations or malfunctations
        '''
        all_mutations = mutations.mutation_list_builder()
        for mutation_name in sorted(persona.Mutations.keys()):
            mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)
            working_mutation = mutuple[1](persona)
            header, details, param = working_mutation.return_details(
                working_mutation.__class__
            )
       
            blob = f"**{header}** - {details}\n{param}"       
            self.set_font("Helvetica", size=9)
            self.multi_cell(0,5,txt= blob, markdown=True,new_x="LEFT",new_y="NEXT",)

        return 

    def anthro_biologic_info(self, persona:AllRecords)->None:
        '''
        prints anthro bio info (NOT mutations)
        '''
        blob = f"**Age:** {persona.Age} years, ({persona.Age_Cat}) **Hite:** {persona.Hite} cms **Wate:** {persona.Wate} kgs ({persona.Size_Cat})"
        self.markdown_internal(blob,11)
        return 

    def alien_biologic_info(self, persona:AllRecords)->None:
        '''
        prints the alien xenologic info 
        '''
        blob = f"**Age:** {persona.Age} {persona.Age_Suffix}, ({persona.Age_Cat}) **Hite:** {persona.Hite} cms **Wate:** {persona.Wate} {persona.Wate_Suffix} ({persona.Size_Cat})"
        self.markdown_internal(blob,11)

        ### Build description column
        desc_column =['Description, detailed '] # heading

        desc_parts = [
            f"Head: {persona.Head} {persona.Head_Adorn}",
            f"Body: {persona.Body} {persona.Body_Adorn}",
            f"Arms: {persona.Arms} {persona.Arms_Adorn}",
            f"Legs: {persona.Legs}",
            " ",
            "Movement legend:",
            f"l=land, a=air, w=water, s=sessile, n=none"
        ]
        desc_column.extend(desc_parts)

        ### build xenobiology column
        xeno_column =['Xenobiology'] # heading
        xeno_column.extend(persona.Biology)

        ### build life cycle column
        life_column = [f"Life Cycle ({persona.Age_Suffix})"] # heading
        for stage_name, values in persona.Life_Stages.items():
            life_column.append(f"{stage_name}: {values[0]} - {values[1]}")

        ### build society column
        soc_column = ["Society"]
        if persona.Society["Tools"] == "Flora or Fauna":
            soc_column.extend(["None:", "Flora / Fauna"])
        else:
            for society_aspect, value in persona.Society.items():
                if value != "None":
                    soc_column.append(f'{society_aspect}: {value}')

        # column balancing
        max_len = max([len(desc_column),len(xeno_column),len(life_column),len(soc_column)]) 
        min_len = min([len(desc_column),len(xeno_column),len(life_column),len(soc_column)]) 
        delta = max_len - min_len

        for columns in [desc_column,xeno_column,life_column,soc_column]:
            if len(columns) < max_len:
                columns += " " * (delta)

        # attack header line
        TABLE_DATA = zip(desc_column,xeno_column,life_column,soc_column)

        # todo calculate the column widths based on longest line in each column
        self.set_font("Helvetica", size=9)
        self.set_fill_color(255)
        with self.table(
            align="LEFT",
            width = 200,
            col_widths=(80, 45, 35, 30),
            text_align="LEFT",
            borders_layout="MINIMAL",
            line_height = 1.2 * self.font_size
            ) as attack_table:
            for data_row in TABLE_DATA:
                row = attack_table.row()
                for datum in data_row:
                    row.cell(str(datum))

        return

    def robot_biologic_info(self, persona:AllRecords)->None:
        '''
        prints the robotic mechanical data
        '''
        blob = f"**Age:** {persona.Age} {persona.Age_Suffix}, ({persona.Age_Cat}) **Hite:** {persona.Hite} cms **Wate:** {persona.Wate} {persona.Wate_Suffix} ({persona.Size_Cat})"
        self.markdown_internal(blob,11)    

        ### build tech spec column
        tech_column = ["Tech Specs"] # title
        tech_column.extend(persona.Spec_Sheet) # from the robot
        tech_column.extend([
            f'Fabricator: {persona.Fabricator}',
            f'Model Name: {persona.Model}',
            f"Base Type: {persona.Base_Family}",
            f"Adaptability: {persona.Adapt}",
            f'Power Plant: {persona.Power_Plant}',
            f'Power Reserve: {persona.Power_Reserve}',
            f"Sensors: {persona.Sensors}",
            f'Value: {persona.Value}',])

        ### build combat column
        combat_column = ["Combat Peripherals"]
        combat_column.append(f'Ram - {exp_tables.ramming_freedom[persona.Ramming]}')
        combat_column.extend(persona.Attacks)
        if persona.Defences:
            combat_column.extend(persona.Defences)


        ### build peripherals column
        peripherals_column = ["Peripherals"]
        if persona.Peripherals:
            peripherals_column.extend(persona.Peripherals)
        else:
            peripherals_column.append("None")

        ### column balancing
        max_len = max([len(tech_column),len(combat_column),len(peripherals_column)]) 
        min_len = min([len(tech_column),len(combat_column),len(peripherals_column)]) 
        delta = max_len - min_len

        for columns in [tech_column,combat_column,peripherals_column]:
            if len(columns) < max_len:
                columns += " " * (delta)   


        # create by zipping
        TABLE_DATA = zip(tech_column,combat_column,peripherals_column)

        # todo calculate the column widths based on longest line in each column
        self.set_font("Helvetica", size=10)
        self.set_fill_color(255)
        with self.table(
            align="LEFT",
            width = 200,
            col_widths=(70, 70, 60),
            text_align="LEFT",
            borders_layout="NONE",
            line_height = 1.2 * self.font_size
            ) as attack_table:
            for data_row in TABLE_DATA:
                row = attack_table.row()
                for datum in data_row:
                    row.cell(str(datum))

        return 

    def family_bio_data(self, persona:AllRecords)-> None:
        ''' pick the family for biuo op'''
        bio_data_pivot = {"Anthro":self.anthro_biologic_info, "Alien":self.alien_biologic_info, "Robot":self.robot_biologic_info}
        bio_data_pivot[persona.FAMILY](persona)
        return

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

    ## sheet support functions
     
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

    def perimiter_box(self)->None:
        '''
        draws a rectangle around entire page 
        MUST BE CALLED LAST FOR Z coverage
        '''
        self.set_draw_color(0, 0, 0) 
        self.set_line_width(1.2)
        self.rect(5, 13, (self.epw - 10), (self.eph - 20), "D")

    def set_or_get(self, *args) -> tuple:
        '''
        takes args and prints variants x,y,location  
        remove the 4 print statements for operations
        ''' 
        if len(args) == 3: # set and tell
            x,y,verbose = args
            print(f'Setting: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f} at {verbose}') # todo turn off for operations 
            self.set_y(y)
            self.set_x(x)

        elif len(args) == 2: # set and don't tell
            x,y = args
            print(f'Setting: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f}') # todo turn off for operations 
            self.set_y(y)
            self.set_x(x)

        elif len(args) == 1: # get and tell and return
            verbose = args[0]
            if verbose == "hide":
                x = self.get_x()
                y = self.get_y()
                return x,y
            else:
                x = self.get_x()
                y = self.get_y()
                print(f'Locating: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f} at {verbose}') # todo  for operations find and remove all set_or_get(Locating:
                return x,y
            
        elif len(args) == 0: # get and don't tell and return 
            x = self.get_x()
            y = self.get_y()
            print(f'Locating: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f}') # todo  for operations find and remove all set_or_get(Locating:          
            return x,y

    def note_lines(self)-> None:
        '''
        draws a chosen number of lines
        '''
        y_bump = 8
        x,y = self.get_x(), self.get_y()
        y += y_bump
        lines = round((279.4 - y)/y_bump)
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

    def sheet_footer(self, persona:AllRecords) -> None:
        '''
        prints the info at page bottom outside perimeter box
        '''
        self.set_font("Helvetica", size=7)
        line_height = self.font_size * 1.6
        self.set_xy(8, 273)
        persona.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())
        blob = f" **Printed:** {persona.Date_Updated} **Created:** {persona.Date_Created} **File:** {persona.File_Name}"
        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=blob,
            align="C",
        )

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

# fix test all PROFs
def attack_table_composer(attack_tabler:exp_tables.PersonaRecord)-> dict:
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
    alien_attacks = attack_tabler.Attacks if attack_tabler.FAMILY == "Alien" else []

    ### define the empty combat dictionary
    attack_table = {
        "A": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "B": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "C": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0}
        }

    ### determine which attack table info is applicable
    if vocation not in ["Alien","Robot"]: # persona has an actual vocation
        # Vocation STRIKE row (Type A)
        ABP = math.ceil((1.5 * awe) + (2 * dex) + (1.5 * intel) + (5 * pstr))
        ABP = ABP + exp_tables.vocation_level_bonus[vocation]["A"] * level
        ABNP = math.ceil(ABP * exp_tables.vocation_non_proficient[vocation]["A"] / 100)
        AMR = 625 + ABP
        ADB = math.ceil(pstr / 2)

        # Vocation FLING row (Type B)
        BBP = awe + (4 * dex) + intel + (2 * pstr)
        BBP = BBP + exp_tables.vocation_level_bonus[vocation]["B"] * level
        BBNP = math.ceil(BBP * (exp_tables.vocation_non_proficient[vocation]["B"] / 100))
        BMR = 650 + BBP
        BDB = math.ceil(pstr / 4)

        # Vocation SHOOT row (Type C)
        CBP = awe + (9 * dex) + intel + pstr
        CBP = CBP + exp_tables.vocation_level_bonus[vocation]["C"] * level
        CBNP = math.ceil(CBP * (exp_tables.vocation_non_proficient[vocation]["C"] / 100))
        CMR = 675 + CBP
        CDB = 0

    elif vocation == "Alien":
        # Alien STRIKE row (Type A)
        if "Strike" in alien_attacks:
            ABP = ABNP = 10 * (pstr + level)
            AMR = 700 + ABP
            ADB = level
        else:
            ABP = ABNP = AMR = ADB = "---"

        # Alien FLING row (Type B)
        if "Fling" in alien_attacks:
            BBP = BBNP = 10 * (dex + level)
            BMR = 700 + BBP
            BDB = level
        else:
            BBP = BBNP = BMR = BDB = "---"

        # Alien SHOOT row (Type C)
        if "Shoot" in alien_attacks:
            CBP = CBNP = 10 * (intel + level)
            CMR = 700 + CBP
            CDB = level
        else:
            CBP = CBNP = CMR = CDB = "---"
        
        # populate the PROF column

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

    ### build the attack table to return
    # assign STRIKE row(ABP, ABNP, AMR, ADB)
    attack_table["A"]["BP"] = ABP
    attack_table["A"]["BNP"] = ABNP
    attack_table["A"]["MR"] = AMR
    attack_table["A"]["ADB"] = ADB
    attack_table["A"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["A"][table_level]

    # assign FLING row (BBP, BBNP, BNR, BDB)
    attack_table["B"]["BP"] = BBP
    attack_table["B"]["BNP"] = BBNP
    attack_table["B"]["MR"] = BMR
    attack_table["B"]["BDB"] = BDB
    attack_table["B"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["B"][table_level]

    # assign SHOOT row (CBP, CBNP, CMR, CDB)
    attack_table["C"]["BP"] = CBP
    attack_table["C"]["BNP"] = CBNP
    attack_table["C"]["MR"] = CMR
    attack_table["C"]["CDB"] = CDB
    attack_table["C"]["PROF"] = exp_tables.vocation_proficiencies[vocation]["C"][table_level]

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

    # assign proficiencies 
    # todo pull proficiencies from proficiencies list in persona record
    APROF = exp_tables.numbers_2_words[APROF] if isinstance(APROF,int) else APROF
    BPROF = exp_tables.numbers_2_words[BPROF] if isinstance(APROF,int) else BPROF
    CPROF = exp_tables.numbers_2_words[CPROF] if isinstance(CPROF,int) else CPROF

    # print out the combat table
    print(f'\nATTACK TABLE: -- {persona.Vocation} Level {persona.Level}')
    print(f'{" ":>6} {"Skill":>6} {"Raw":>6} {"Max":>6} {"Force":>6} {"PROF":>5}')
    print(f"Strike {ABP:>6} {ABNP:>6} {AMR:>6} {ADB:>6}  {APROF}")
    print(f"Fling  {BBP:>6} {BBNP:>6} {BMR:>6} {BDB:>6}  {BPROF}")
    print(f"Shoot  {CBP:>6} {CBNP:>6} {CMR:>6} {CDB:>6}  {CPROF}")

    if persona.FAMILY == 'Alien':
        blob = f'Attack Description: {persona.Attack_Desc} \nMOVE:  land {persona.Move_Land} h/u, air {persona.Move_Air} h/u, water {persona.Move_Water} h/u. ARMOUR RATING: {persona.AR}'      
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

def alien_screen(screenery:exp_tables.PersonaRecord) -> None:
    """
    screen prints alien persona
    """

    # clearance for Clarence
    please.clear_console()

    print(
        f"\nALIEN PERSONA RECORD\n"
        f"Persona: {screenery.Persona_Name} \t\tPlayer Name: {screenery.Player_Name} \tCreated: {screenery.Date_Created}\n"
        f"AWE: {screenery.AWE} CHA: {screenery.CHA} CON: {screenery.CON} DEX: {screenery.DEX} "
        f"INT: {screenery.INT} MSTR: {screenery.MSTR} PSTR: {screenery.PSTR} HPS: {screenery.HPM} SOC: {screenery.SOC} WA: {screenery.WA}\n"
        f"Family: {screenery.FAMILY} Species: {screenery.FAMILY_TYPE}\n"
        f"Age: {screenery.Age} {screenery.Age_Suffix} Size: {screenery.Size_Cat} Wate: {screenery.Wate} {screenery.Wate_Suffix}"
    )

    # vocation, level, EXPS
    if screenery.Vocation == "Alien":
        print(f"{screenery.FAMILY_SUB} Level: {screenery.Level} EXPS: {screenery.EXPS}")
    else:    
        print(f"Vocation: {screenery.Vocation} Level: {screenery.Level} EXPS: {screenery.EXPS}")

    print(f"\nDESCRIPTION: {screenery.Quick_Description}")

    # four part description
    # the split removes the (l,a,w) movement info
    print(f"{screenery.Head.split(' (')[0]} head {screenery.Head_Adorn}")
    print(f"{screenery.Body.split(' (')[0]} body {screenery.Body_Adorn}")
    print(f"{screenery.Arms.split(' (')[0]} arms {screenery.Arms_Adorn}")
    print(f"{screenery.Legs.split(' (')[0]} legs")

    # show the attack table
    screen_attack_table(screenery)

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
    print(f"\nNATURAL POWERS: ", end='')

    if len(screenery.Mutations) == 0:
        print("None")
    else:
        print()
        all_mutations = mutations.mutation_list_builder()
        for mutation_name in screenery.Mutations.keys():
            mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)
            working_mutation = mutuple[1](screenery)
            working_mutation.post_details(working_mutation.__class__)

    print(f"\nBIOLOGY of {screenery.FAMILY_SUB}")
    for bio_line in screenery.Biology:
        print(f"{bio_line}")
    print()


    for stage,tuple_ in screenery.Life_Stages.items():
        if stage == "Life Span":
            print(f'LIFE SPAN: {tuple_[1]} {screenery.Age_Suffix}')
        else:    
            print(f"{stage} {tuple_[0]} to {tuple_[1]} {screenery.Age_Suffix}")

    print(f"\nSOCIETY of {screenery.FAMILY_TYPE}")
    for element,value in screenery.Society.items():
        if element == "Tool":
            print(f'Tool Usage: {value}')
        elif element == "Language":
            if value == "None":
                print(f'No language: {screenery.Sounds}')
            else:
                print(f'Language of {screenery.Sounds}')
        else:
            if value != "None":
                print(f'{element}: {value}')
        

    if screenery.RP_Cues:
        print("\nROLE-PLAYING CUES:")
        for fun in screenery.RP_Fun:
            print(f"{fun}")

#####################################
# ROBOT output to screen
#####################################

def robot_screen(bot_screen: exp_tables.PersonaRecord) -> None:
    """
    print the robot to screen
    """

    # clearance for Clarence
    please.clear_console()

    print(f'\n\nROBOT PERSONA RECORD - {bot_screen.FAMILY_TYPE.upper()} {bot_screen.FAMILY_SUB.upper() if bot_screen.FAMILY_SUB else ""}')
    print(
        f"Name: {bot_screen.Persona_Name} \t\tPlayer Name: {bot_screen.Player_Name} Created: {bot_screen.Date_Created}\n"
        f"AWE: {bot_screen.AWE} CHA: {bot_screen.CHA} CON: {bot_screen.CON}({bot_screen.CON_Prime}) "
        f"DEX: {bot_screen.DEX}({bot_screen.DEX_Prime}) INT: {bot_screen.INT}({bot_screen.INT_Prime}) "
        f"MSTR: {bot_screen.MSTR} PSTR: {bot_screen.PSTR}({bot_screen.PSTR_Prime}) HPS: {bot_screen.HPM}\n"
    )

    print("APPEARANCE:")
    print(f"{bot_screen.Quick_Description} \nSize: {bot_screen.Size_Cat} Wate: {bot_screen.Wate} {bot_screen.Wate_Suffix} Hite: {bot_screen.Hite} {bot_screen.Hite_Suffix}")

    # build mechanicals for consistency 
    mechanicals = []
    mechanicals.append(f'Robot Type: {bot_screen.FAMILY_TYPE}')
    if bot_screen.FAMILY_SUB:
        mechanicals.append(f'Robot Sub Type: {bot_screen.FAMILY_SUB}')
    mechanicals.append(f"Base Family:  {bot_screen.Base_Family} ")
    mechanicals.append(f'Model Name: {bot_screen.Model}')
    mechanicals.append(f'Manufacturer: {bot_screen.Fabricator}')
    mechanicals.append(f'Control Factor: {bot_screen.CF}')
    mechanicals.append(f"Adaptability: {bot_screen.Adapt}")
    mechanicals.append(f"Power Plant: {bot_screen.Power_Plant}")
    mechanicals.append(f"Power Reserve: {bot_screen.Power_Reserve} months")
    mechanicals.append(f"Sensors: {', '.join(bot_screen.Sensors)}")
    mechanicals.append(f"Locomotion: {bot_screen.Locomotion}")   

    please.enumerate_this("\nMECHANICALS: ", mechanicals, False)

    please.enumerate_this("\nSPEC SHEET: ", bot_screen.Spec_Sheet, False)

    please.enumerate_this("\nATTACKS: ", bot_screen.Attacks)

    please.enumerate_this("\nDEFENCES: ", bot_screen.Defences)

    please.enumerate_this("\nPERIPHERALS: ", bot_screen.Peripherals)

    print("\nANOMALIES: ", end=" ")

    if len(bot_screen.Mutations) == 0:
        print("None")

    else:
        all_mutations = mutations.mutation_list_builder()
        for mutation_name in bot_screen.Mutations.keys():
            mutuple = next((t for t in all_mutations if t[0] == mutation_name), None)
            working_mutation = mutuple[1](bot_screen)
            working_mutation.post_details(working_mutation.__class__)

    # show the combat table
    screen_attack_table(bot_screen)

    if bot_screen.Vocation != "Robot":
        print("\nRobots do not get a VOCATION COMBAT TABLE. Sorry.\n")
        # robot vocation Gifts
        gift_list = vocation.update_gifts(bot_screen)
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


    if bot_screen.RP_Cues:
        print("\nROLE-PLAYING CUES:")
        for fun in bot_screen.RP_Fun:
            print(f"{fun}")

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

    if persona.RP_Cues:
        print("\nROLE-PLAYING CUES:")
        for fun in persona.RP_Fun:
            print(f"{fun}")

#####################################
# TOY output to screen
#####################################

def toy_screen(blank:any) -> None:
    '''prints out a toy to the screen'''
    pass
    
#####################################
#
# PDF testing
#
#####################################


""" 
those fucking proficiencies
ANTHROS assigned by
    APROF = exp_tables.vocation_proficiencies[vocation]["A"][table_level]
    if APROF = 42:
        if vocation == "Mercenary":
            APROF = "All weapons"
        else: # this would be Nothing
            APROF = "One weapon only"

    BPROF = exp_tables.vocation_proficiencies[vocation]["B"][table_level]
    CPROF = exp_tables.vocation_proficiencies[vocation]["C"][table_level]

ROBOTS 
    APROF = BPROF = CPROF = "Robots have no weapon skills."

ALIENS 
    APROF = BPROF = CPROF = "Natural."
"""
