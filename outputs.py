import math
import os
import time
import webbrowser
import sys
import re
import inspect

from fpdf import FPDF
from dataclasses import dataclass
from typing import Tuple, Union
from collections import Counter

import alien
import please
import mutations
import vocation
import exp_tables

# todo RP combat block: weak strong cannon fodder, canon fodder and canonical

@dataclass 
class AllRecords(exp_tables.AllThings):
    pass

def outputs_workflow(outputter:AllRecords, out_type: str) -> None:
    '''
    divides outputs between screen and pdf
    '''
    out_type = "screen" if out_type not in ["pdf","screen"] else out_type


    if out_type == "pdf":
        bespoke_pdf_chooser(outputter)

    elif out_type == "screen":
        please.screen_this(outputter)

    return None

################################################
#
# (f)laws of fpdf
#
################################################
'''
UNITS:
    x,y and lengths are FLOATS in mm (millimeters)
    font sizes are in POINTS not mm or pixels

    PostScript typographical measurement system
    a POINT is 1/72 of an inch not mm or pixels
    1 point = 1pt = 1/72in (calc) = 0.3528 mm

    there are 25.4016 mm in 1 inch
    12 point font is 4.23 mm
    arial 12 space = 1.8 mm 

US LETTER:  
    width (x) 215.9 mm, height (y) = 279.4 mm
    epw() = effective page width = 215.9 mm
    eph() = effective page hite = 279.4 mm
 
COORDS
    origin point = (0, 0) = Left, Top corner
    x-coordinate increases moves RIGHT
    y-coordinate increases moves DOWN 

    x,y are top left of BOUNDING BOX not center of polygons/lines
    bounding box is NOT square and changes with polygon orientation
'''

################################################
#
# classes for pdf creation
#
################################################

class PDF(FPDF):

    ## persona output functions 

    def persona_title(self, blob: str = 'where da blob', font_size: int = 12)-> None:
        '''prints PERSONA NAME above perimeter box left justified'''
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
        line_height = self.font_size * 1.4
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


    def markdown_robot_decay(self, blob: str = 'where da blob',font_size: int = 14)-> None:
        '''
        a cell modified for markdown with default font_size
        '''

        self.set_font("courier",size=font_size)
        line_height = self.font_size * 1.4
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
        prints attribute acronyms, values (+/- primes) and descriptions (+/-)
        """

        # for the pain
        awe, cha, con, dex, intel, mstr, pstr, soc, hpm = persona.AWE, persona.CHA,  persona.CON, persona.DEX, persona.INT, persona.MSTR, persona.PSTR, persona.SOC, persona.HPM

        # prep for Alien and Anthro, Robot is different
        not_bot = True if persona.FAMILY in ["Alien", "Anthro"] else False


        con_footer = "Constitution" if not_bot else f"Constitution-P{persona.CON_Prime}"
        dex_footer = "Dexterity" if not_bot else f"Dexterity-P{persona.DEX_Prime}"
        intel_footer = "Intelligence" if not_bot else f"Intelligence-P{persona.INT_Prime}"
        pstr_footer = "Strength" if not_bot else f"Strength-P{persona.PSTR_Prime}"
        mstr_title, mstr_value, mstr_footer = "MND", mstr, "Mind"

        if persona.FAMILY == "Robot":
            mstr_title = "CF"
            mstr_value = persona.CF
            mstr_footer = "Autonomy"

        TABLE_DATA = [
            ["AWE", "CHA", "CON", "DEX", "INT", mstr_title, "STR", "SOC", "HPM", ("Helvetica", "B", 14)],
            [awe, cha,  con, dex, intel, mstr_value, pstr, soc, hpm,("Helvetica", "",18)],
            ["Awareness", "Charisma", con_footer, dex_footer, intel_footer, mstr_footer, pstr_footer, "Privilege", "Resilience", ("Helvetica","B", 7)]
        ]

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
                    markdown=True,
                    txt=datum, 
                    border=False, 
                    align='C',    
                    new_x="RIGHT",
                    new_y="LAST",
                    )
            top += row_height
            self.set_or_get(start_right,top,"new line")

    def attributes_table_blank(self) -> None:
        """
        prints attribute acronyms, and blanks only works for anthro
        """

    
        # prep for Alien and Anthro, Robot is different




        TABLE_DATA = [
            ["AWE", "CHA", "CON", "DEX", "INT", "MND", "STR", "SOC", "HPM", ("Helvetica", "B", 14)],
            ["___", "___",  "___", "___", "___", "___", "___", "___", "___",("Helvetica", "",18)],
            ["Awareness", "Charisma", "Constitution", "Dexterity", "Intelligence", "Mind", "Strength", "Privilege", "Resilience", ("Helvetica","B", 7)]
        ]

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
                    markdown=True,
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
        return f'{persona.Vocation} level {persona.Level}  EXPS {persona.EXPS}/{vocation.level_goal(persona)}'

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
            ("TYPE", "SKILLED", "RAW", "MAX", "FORCE", "Skills", f"HIT POINTS  ({persona.HPM})"),
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
        blob = f"**Age:** {persona.Age:.2e} {persona.Age_Suffix}, ({persona.Age_Cat}) **Hite:** {persona.Hite} {persona.Hite_Suffix} **Wate:** {persona.Wate} {persona.Wate_Suffix} ({persona.Size_Cat})"
        self.markdown_internal(blob,11)    

        ### build usage spec column
        user_column = ["Usage Specs"]
        user_column.extend(persona.Spec_Sheet) # from the robot

        ### build tech spec column

        ### prebuild sensors string
        sensors_dict = Counter(persona.Sensors)
        sensors_list = "  "
        for sens,amt in sensors_dict.items():
            sensors_list += f'{sens}-{amt} '

        tech_column = ["Tech Specs"] # title
        tech_column.extend([
            f'Fabricator: ',
            f'  {persona.Fabricator}',
            f'Model Name:',
            f'  {persona.Model}',
            f"Base Type",
            f"  {persona.Base_Family}",
            f"Adaptability: {persona.Adapt}",
            f'Power Plant: {persona.Power_Plant}',
            f'Power Reserve: {persona.Power_Reserve} months',
            f"Sensors:",
            f"{sensors_list}",
            f'Value: {persona.Value}',])

        ### build combat column
        combat_column = ["Combat Specs"]
        combat_column.append(f'Ramming Lvl ({persona.Ramming}):')
        combat_column.append(f'  {exp_tables.ramming_freedom[persona.Ramming]}')
        combat_column.extend(persona.Attacks)

        input(f'func = {inspect.currentframe().f_code.co_name} // {combat_column = }')

        # weapons that too long need to be split for pdf op
        # these are ["Vibro", "Inertia", "Electro", "Stun"] attacks

        for index, splitter in enumerate(combat_column):
            if any(target in splitter for target in ["Vibro", "Inertia", "Electro", "Stun"]):
                attack_name, attack_specs = splitter.split(";",1) # splint the too long element
                combat_column[index] = attack_name + ";"
                combat_column.insert(index + 1, f'  {attack_specs}')

        if persona.Defences:
            combat_column.extend(persona.Defences)

        ### build peripherals column
        peripherals_column = ["Peripherals"]
        if persona.Peripherals:
            peripherals_column.extend(persona.Peripherals)
        else:
            peripherals_column.append("None")

        ### column Height balancing
        max_len = max([len(user_column),len(tech_column),len(combat_column),len(peripherals_column)]) 
        min_len = min([len(user_column),len(tech_column),len(combat_column),len(peripherals_column)]) 
        delta = max_len - min_len

        for columns in [user_column, tech_column, combat_column, peripherals_column]:
            if len(columns) < max_len:
                columns += " " * (delta)   

        # create by zipping
        TABLE_DATA = zip(user_column,tech_column,combat_column,peripherals_column)

        self.set_font("Helvetica", size=10)
        self.set_fill_color(0)
        set_columns = (50,50,60,40)
        with self.table(
            align="LEFT",
            width = sum(set_columns),
            col_widths=set_columns,
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
        ''' pick the family for bio op'''
        bio_data_pivot = {"Anthro":self.anthro_biologic_info, "Alien":self.alien_biologic_info, "Robot":self.robot_biologic_info}
        bio_data_pivot[persona.FAMILY](persona)
        return

    def referee_persona_fun(self,persona)-> None:
        '''
        prints referee persona role playing suggestions
        '''
        for fun in persona.RP_Fun:
            self.markdown_internal(fun,11)

        return

    ### sheet support functions
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

    def locutus(self) -> None:
        """
        Draws a target at x and y on the page.
        """
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.3)  # Set line width.

        # Make a green circle around locutus
        self.set_draw_color(0, 255, 0)  # Green
        radius = 15
        self.circle(
            x,       # Use x directly as the center
            y,       # Use y directly as the center
            radius,  # Radius of the circle
            "D",
        )

        # Draw a blue cross centered at (x, y)
        centering = radius / 2
        self.set_draw_color(0, 0, 255)  # Blue
        self.line(x - centering, y - centering, x + centering, y + centering)  # Diagonal line 1
        self.line(x - centering, y + centering, x + centering, y - centering)  # Diagonal line 2


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
        # show values prints x and y data to screen as pdf gets built
        show_values = False # change to false for operations

        if len(args) == 3: # set and tell
            x,y,verbose = args
            if show_values:
                print(f'Setting: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f} at {verbose}') 
            self.set_y(y)
            self.set_x(x)

        elif len(args) == 2: # set and don't tell
            x,y = args
            if show_values:
                print(f'Setting: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f}') 
            self.set_y(y)
            self.set_x(x)

        elif len(args) == 1: # get and tell and return
            verbose = args[0]
            if show_values == "hide":
                x = self.get_x()
                y = self.get_y()
                return x,y
            else:
                x = self.get_x()
                y = self.get_y()
                if show_values:
                    print(f'Locating: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f} at {verbose}') 
                return x,y
            
        elif len(args) == 0: # get and don't tell and return 
            x = self.get_x()
            y = self.get_y()
            if show_values: 
                print(f'Locating: LEFT(x) = {x:.1f}, TOP(y) = {y:.1f}')           
            return x,y

    def note_lines_specific(self,lines)-> None:
        '''
        draws a chosen number of lines
        '''

        x,lines_y = self.get_x(), self.get_y()
        top,left = self.set_or_get("inside note lines specific")

        y_bump = 8
        lines_y += y_bump
        max_y = lines_y + y_bump * lines
        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)
        while lines_y < max_y:
            self.line(8,lines_y, 210, lines_y)
            self.set_or_get(8,lines_y,"new line")

            lines_y += y_bump

    def note_lines(self)-> None:
        '''
        draws a chosen number of lines
        '''
        y_bump = 8
        x,y = self.get_x(), self.get_y()
        top,left = self.set_or_get("inside note lines")

        y += y_bump
        lines = round((278 - y)/y_bump)
        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)

        for more_y in range(int(y),int(y+y_bump*lines),8):
            self.line(8, more_y, 210, more_y)

    def equipment_lines(self, persona, lines)->None:
        '''
        prints weight allowance and equipment title lines
        draws split lines for equipment
        '''
        left,top = self.set_or_get("inside equipment lines")
        # prepare equipment lines
        self.set_draw_color(120) #dark grey 
        self.set_line_width(0.1)
        
        # output equipment lines
        bump = 8
        for top in range(int(top+bump),int(top+bump*lines),bump):
            self.line(8, top, 69,top) # item
            self.line(73,top, 86,top) # wt
            self.line(90,top, 103,top) # ttl
            self.line(107,top, 208,top) # info
        self.set_or_get(6.4,top,"reset inside equipment lines")
        return 
    
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

    def hexagons(self, size=10, width=210, hite=260) -> None:
        ''' fill it with sexagons
            actual width=216, hite=279
            modified for inner border
        
        '''
        polywanna = size
        apothem = polywanna * math.sqrt(3) / 2
        col_number = round(width/apothem) - 1
        row_number = round(hite/(apothem*(apothem/polywanna)))

        y = polywanna + 15
        x_off = 6

        self.set_line_width(0.45)
        self.set_draw_color(80)

        for row in range(1,row_number):
            x = (apothem/2)+x_off if row % 2 == 0 else x_off #start value x: odd at page, even offset 
            for col in range(0,col_number):
                self.regular_polygon(x, y, polyWidth=polywanna, rotateDegrees=270, numSides=6, style="D")
                x += apothem
            y += apothem*(apothem/polywanna)
        #print(f"{row = } {col = } {hite = } {width = }")

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
    file_dos = r'C:\Users\mobil\Documents\EXP_Game_Tools\Records\Bin\37bf560f9d0916a5467d7909.pdf'
    print(f"\nPlease wait. Composing PDF and sending to browser\nTemp file is at: {file_dos}")
    try:
        for root, _, files in os.walk(search_path):
            if file_name in files:
                found_file = os.path.join(root, file_name)
                browser_file = "file:///" + found_file.replace('\\','/')
                webbrowser.get('windows-default').open_new('file:///C:/Users/mobil/Documents/EXP_Game_Tools/Records/Bin/37bf560f9d0916a5467d7909.pdf')
                break
    except PermissionError:
        print(f"Permission denied for directory {root}. Continuing search...")
    except Exception as e:
        print(f"An error occurred: {e}")

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
            ABP = ABNP = AMR = ADB = "  -"

        # Alien FLING row (Type B)
        if "Fling" in alien_attacks:
            BBP = BBNP = 10 * (dex + level)
            BMR = 700 + BBP
            BDB = level
        else:
            BBP = BBNP = BMR = BDB = "  -"

        # Alien SHOOT row (Type C)
        if "Shoot" in alien_attacks:
            CBP = CBNP = 10 * (intel + level)
            CMR = 700 + CBP
            CDB = level
        else:
            CBP = CBNP = CMR = CDB = "  -"
        
        # populate the PROF column

    elif family == "Robot":
        # specific robot attributes
        pstr_prime = attack_tabler.PSTR_Prime
        dex_prime = attack_tabler.DEX_Prime
        intel_prime = attack_tabler.INT_Prime

        # Robot STRIKE row (Type A)
        ABP = (5 * dex) + (5 * intel) + (pstr_prime * pstr) + (level * pstr)
        ABNP = 0
        AMR = "  -"
        ADB = pstr

        # Robot FLING row (Type B)
        BBP = (5 * awe) + (5 * pstr) + (dex_prime * dex) + (level * dex)
        BBNP = 0
        BMR = "  -"
        BDB = math.ceil(pstr / 2)

        # Robot SHOOT row (Type C)
        CBP = (5 * awe) + (5 * dex) + (intel_prime * intel) + (level * intel)
        CBNP = 0
        CMR = "  -"
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

    # these lines are for ease of reading and debugging 
    # A = strike B = fling C = shoot
    # BP = Skilled BNP = Raw MR = Max DB = Force PROF = Skills
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
    print(f'\nATTACK TABLE:    {persona.Vocation} Level {persona.Level}')
    print(f'{" ":>6} {"Skill":>6} {"Raw":>6} {"Max":>6} {"Force":>6} {"PROF":>5}')
    print(f"Strike {ABP:>6} {ABNP:>6} {AMR:>6} {ADB:>6}  {APROF}")
    print(f"Fling  {BBP:>6} {BBNP:>6} {BMR:>6} {BDB:>6}  {BPROF}")
    print(f"Shoot  {CBP:>6} {CBNP:>6} {CMR:>6} {CDB:>6}  {CPROF}")

    if persona.FAMILY == 'Alien':
        blob = f'Attack Description: {persona.Attack_Desc} \nMOVE:  land {persona.Move_Land} h/u, air {persona.Move_Air} h/u, water {persona.Move_Water} h/u. DEFENCE RATING: {persona.AR}'      
    else:
        blob = f'MOVE:  {persona.Move} h/u  DEFENCE RATING: {persona.AR}'

    print(blob)    

    return

#####################################
#  PDF print outs
#####################################

def blank_pdf_chooser() -> None:
    """
    choose from blank PDFs for printint purposes
    """

    blank_pdf_function_map = {
        "Anthro Player":anthro_blank_pdf,
        "Alien Player":anthro_blank_pdf,
        "Robot Player":anthro_blank_pdf
    }

    please.clear_console()
    choice_comment = "Choose a blank PDF"
    choices = list(blank_pdf_function_map.keys())
    blank_pdf_choice = please.choose_this(choices,choice_comment)

    ###  PDF page prep
    pdf = PDF(orientation="P", unit="mm", format=(215.9, 279.4))
    pdf.set_margin(0)
    pdf.set_auto_page_break(False)
    pdf.add_page()
    
    if blank_pdf_choice in blank_pdf_function_map:
        blank_pdf_function_map[blank_pdf_choice](pdf)

    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )


def bespoke_pdf_chooser(persona) -> None:
    '''
    choose between pdf styles
    '''
    choice_list = [
        "Persona One Shot",
        "Persona Campaign",
        "Campaign Sheet",
    ]
    pdf_chosen  = please.choose_this(choice_list, "PDF type needed? ")

    ###  PDF page prep
    pdf = PDF(orientation="P", unit="mm", format=(215.9, 279.4))
    pdf.set_margin(0)
    pdf.set_auto_page_break(False)
    pdf.add_page()

    ### PDF output 
    if pdf_chosen == "Persona One Shot":
        record_front(pdf, persona, one_shot=True)
    elif pdf_chosen == "Persona Campaign":
        record_front(pdf,persona,one_shot=False)
    elif pdf_chosen == "Campaign Sheet":
        campaign_sheet(pdf, persona, one_shot=False)
    else:
        print("what the hell dude")

    ### PDF store and output
    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )
    show_pdf()

def wate_allowance(pdf,persona)->None:
    '''
    wate allowance output for personas
    four settings: anthro, robot, alien, and feral
    '''

    # wate allowance title stripe
    pdf.set_or_get(5.4,17.5, "before WA Stripe")
    pdf.section_title(f"WATE ALLOWANCE", f"{persona.WA} kg for {persona.FAMILY} with move {persona.Move} h/u")
    left,top = pdf.set_or_get("after WA stripe")

    pdf.set_or_get(6.4,top+6.5, "before WA comment")
    if persona.FAMILY == "Anthro":
        pdf.markdown_internal(f"Sprint ({persona.Move*2} h/u): **<{persona.WA/4} kg** Carry ({persona.Move} h/u): **<{persona.WA*1.5} kg.  Lift Max (0 h/u): **{persona.WA*2.5}kg.**")

    elif persona.FAMILY == "Robot":
        pdf.markdown_internal(f"Full ({persona.Move} h/u): **<{persona.WA} kg** Stopped (0 h/u): **{persona.WA}kg.**")

    elif persona.FAMILY == "Alien":
        # "Move_Land": 7, "Move_Air": 4, "Move_Water": 4 "Move":14
        WA, base_move, land_move, air_move, water_move = persona.WA, persona.Move, persona.Move_Land, persona.Move_Air, persona.Move_Water

        if persona.Society["Tools"] == "Flora or Fauna":
            pdf.markdown_internal(f"Flora or Fauna can carry, push or pull objects. They cannot use them.",12)

        if land_move > 0:
            pdf.markdown_internal(f"**Land:** Free {land_move} h/u: **<{round(WA*land_move/base_move/2)} kg**  Carry {land_move/2} h/u: **<{round(WA*land_move/base_move)} kg** Lift 0 h/u: **{round(WA*land_move/base_move)} kg**",12)
        if air_move > 0:   
            pdf.markdown_internal(f"**Air:** Free {air_move} h/u: **<{round(WA*air_move/base_move/2)} kg**  Carry {air_move/2} h/u: **<{round(WA*air_move/base_move)} kg** Lift 0 h/u: **{round(WA*air_move/base_move)} kg**",12)
        if water_move > 0:   
            pdf.markdown_internal(f"**Water:** Free {water_move} h/u: **<{round(WA*water_move/base_move/2)} kg**  Carry {water_move/2} h/u: **<{round(WA*water_move/base_move)} kg** Lift 0 h/u: **{round(WA*water_move/base_move)} kg**",12)

    left,top = pdf.set_or_get("after wate allowance") # todo is this needed?
    return

def toy_output(pdf,persona,lines=15)->None:
    '''
    output the TOYS stripe and follow with toy lines 
    '''
    left,top = pdf.set_or_get()
    pdf.set_or_get(5.4,top)
    pdf.section_title(f"TOYS", "Technological Object Yield System")
    left,top = pdf.set_or_get("after TOYS  stripe")

    # equipment list header
    pdf.set_or_get(6.4,top+6.5, "before equipment lines ")
    pdf.markdown_internal(f'**ITEM**{" "*40}**WT**{" "*7}**TTL**{" "*7}**INFO**')
    left,top = pdf.set_or_get()
    pdf.equipment_lines(persona,lines)

def notes_output(pdf)->None:
    '''
    output the NOTES stripe and follow with lines to bottom
    '''
    # notes info stripe
    left,top = pdf.set_or_get("arriving at notes_output")
    pdf.set_or_get(5.4, top,"before NOTE stripe")
    pdf.section_title("NOTES", f" ")
    left,top = pdf.set_or_get("after NOTE stripe ")

    # make some lines
    pdf.set_or_get(5.4, top +8,"before lines")
    pdf.note_lines()
    left,top = pdf.set_or_get("after note lines ")

def record_front(pdf, persona, one_shot)->None:
    '''
    organizes print out of all persona data on one page
    '''

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD** for {persona.Persona_Name}",18)

    # player title right justified
    right_text = f"**Player:** {persona.Player_Name}"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # attributes stripe
    pdf.set_or_get(5.4,17.5, "attribute stripe")
    pdf.section_title("ATTRIBUTES", persona.Quick_Description)
    left,top = pdf.set_or_get("after attribute stripe")

    # attributes table
    pdf.set_or_get(6.4,top+8,"before attributes table")
    pdf.attributes_table(persona)
    left, top = pdf.set_or_get("after attributes table")

    # combat info stripe
    pdf.set_or_get(5.4, top + 2.3,"before combat into title")
    pdf.section_title("COMBAT INFO", pdf.persona_level_info(persona))
    left,top = pdf.set_or_get("after combat table info")

    # movement and AR line
    pdf.set_or_get(6.4,top +7.2, "before move AR line")
    moving = f'{persona.Move} h/u' if persona.FAMILY in ["Anthro", "Robot"] else f'land {persona.Move_Land} h/u, air {persona.Move_Air} h/u, water {persona.Move_Water} h/u.'
    pdf.markdown(f'**MOVE RATE** {moving}  **DEFENCE RATING (DEF)** {persona.AR}  **____  ____**')
    left,top = pdf.set_or_get("after move AR line")

    # attack table title
    pdf.set_or_get(6.4, top + 6.8, "before attack table title")
    pdf.markdown("**ATTACK TABLE**")
    left,top = pdf.set_or_get("after attack table title")

    # attack table, skills, HPS
    pdf.set_or_get(7.2,top + 7, "before attack table") # correct left for centering of table elements
    pdf.attack_table_pdf(persona)
    left,top = pdf.set_or_get("after attack table")

    # if alien show attack description
    if persona.FAMILY == "Alien":
        pdf.set_or_get(6.4,top + 2.6, "before alien attack desc") # correct left for centering of table elements
        pdf.markdown_internal(f'**Attack Description: {persona.Attack_Desc}**', 11)
        left,top = pdf.set_or_get("after alien attack desc")

    # if player show attack table explainer
    if not persona.RP:
        pdf.set_or_get(6.4, top+1, "before attack table explainer")
        pdf.attack_table_explainer()
        left,top = pdf.set_or_get("after attack table explainer")

    # bio info stripe
    pdf.set_or_get(5.4, top + 2.3,"before bio info title")
    bio_title = "BIO INFO" if persona.FAMILY in ["Anthro","Alien"] else "MECH INFO"
    pdf.section_title(bio_title, pdf.persona_bio_info(persona))
    left,top = pdf.set_or_get("after bio info info title")

    # persona bio data
    pdf.set_or_get(6.2,top+6.5,f"before {persona.FAMILY} bio list")
    pdf.family_bio_data(persona)
    left,top = pdf.set_or_get(f"after {persona.FAMILY} bio list")

    # mutations header
    pdf.set_or_get(6.2, top,"before mutation header")
    pdf.mutation_header(persona)
    left,top = pdf.set_or_get("after mutation header")

    # mutations list
    if len(persona.Mutations) > 0:
        pdf.set_or_get(6.4,top+0.3,"before mutation list")
        pdf.mutation_list(persona)
        left,top = pdf.set_or_get("after mutation list")

    # task info stripe
    pdf.set_or_get(5.4, top + 2.3,"before task info title")
    pdf.section_title("TASK INFO", pdf.persona_level_info(persona))
    left,top = pdf.set_or_get("after task info title")

    # persona task info
    pdf.set_or_get(5.4, top + 7.0,"before task info ")
    pdf.task_info(persona)
    left,top = pdf.set_or_get("after task info ")

    # persona task addendum
    pdf.set_or_get(5.4, top,"before task addendum ")
    pdf.task_info_addendum(persona)
    left,top = pdf.set_or_get("after task addendum ")

    # space for notes check
    '''if enough space for notes and lines print notes and lines '''

    if persona.RP_Cues:
        # RP Fun stripe
        pdf.set_or_get(5.4, top + 2.3,"before RP Fun Stripe")
        pdf.section_title("REFEREE PERSONA CUES", persona.Persona_Name)
        left,top = pdf.set_or_get("after RP Fun Stripe")

        # RP Cues
        pdf.set_or_get(5.4, top + 7.0,"before RP Fun")
        pdf.referee_persona_fun(persona)
        left,top = pdf.set_or_get("after RP Fun")


    if 280 - top > 40 and one_shot:
        notes_output(pdf)

    pdf.sheet_footer(persona)
    pdf.perimiter_box() # must go last for z level

    record_back(pdf, persona, one_shot)

def anthro_blank_pdf(pdf)->None:
    '''
    organizes print out of a  blank anthro persona record
    '''

    input(f"you are at anthro_blank_pdf")

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD**",18)

    # player title right justified
    right_text = f"**Player:** _________________"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # attributes stripe
    pdf.set_or_get(5.4,17.5, "attribute stripe")
    pdf.section_title("ATTRIBUTES", " ")
    left,top = pdf.set_or_get("after attribute stripe")

    # attributes table
    pdf.set_or_get(6.4,top+8,"before attributes table")
    pdf.attributes_table_blank()
    left, top = pdf.set_or_get("after attributes table")


    # bio info stripe
    pdf.set_or_get(5.4, top + 2.3,"before bio info stripe")
    bio_title = "BIO INFO"
    pdf.section_title(bio_title, "FAMILY:                GENUS:                     SPECIES:")
    left,top = pdf.set_or_get(f"after bio info stripe\n")

    # persona bio data
    pdf.set_or_get(6.2,top+8,f"before Anthro bio info")
    blob = f"**Age:** ______ **Hite:** ______  **Wate:** ______"
    pdf.markdown_internal(blob,12)
    left,top = pdf.set_or_get(f"after Anthro bio info\n")

    pdf.set_or_get(8,top,f"before the specific lines")
    pdf.note_lines_specific(4)
    left,top = pdf.set_or_get(f"after specific lines\n")

    # task info stripe
    pdf.set_or_get(5.4, top + 2.3,"before task info stripe")
    pdf.section_title("TASK INFO", "VOCATION:  ")
    left,top = pdf.set_or_get(f"after task info stripe\n")

    # persona task info
    pdf.set_or_get(8, top + 7.0,"before task info ")

    blob = f"**GIFTS                        INTERESTS                   SKILLS**"
    pdf.markdown_internal(blob,12)
    left,top = pdf.set_or_get(f"after task info\n")

    pdf.set_or_get(8,top,f"before the specific lines")
    pdf.note_lines_specific(3)
    left,top = pdf.set_or_get(f"after specific lines\n")

    # persona task addendum
    pdf.set_or_get(5.4, top,"before task addendum ")

    blob = f'**Gifts:** Specific task. Auto success. **Interests:** General knowledge (+1) **Skills:** Specific knowledge/task (+2)'
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0,5,txt= blob, markdown=True,new_x="LEFT",new_y="NEXT",)

    left,top = pdf.set_or_get(f"after task addendum\n")

    # combat info stripe
    pdf.set_or_get(5.4, top + 2.3,"before combat into title")
    pdf.section_title("COMBAT INFO", " ")
    left,top = pdf.set_or_get("after combat table info")

    # movement and AR line
    pdf.set_or_get(6.4,top +7.2, "before move AR line")
    pdf.markdown(f'**MOVE RATE** ____ h/u  **DEFENCE RATING (DEF)** ____ ____  ____**')
    left,top = pdf.set_or_get("after move AR line")

    # attack table title
    pdf.set_or_get(6.4, top + 6.8, "before attack table title")
    pdf.markdown("**ATTACK TABLE**")
    left,top = pdf.set_or_get("after attack table title")

    # attack table, skills, HPS
    pdf.set_or_get(7.2,top + 7, "before attack table") # correct left for centering of table elements

    # attack header line
    TABLE_DATA = (
        ("TYPE", "SKILLED", "RAW", "MAX", "FORCE", "Skills", f"HIT POINTS"),
        ("Strike", "______","______", "______", "___","__________________________",""),
        ("Fling", "______","______", "______", "___","__________________________",""),
        ("Shoot", "______","______", "______", "___","__________________________","")
    )

    pdf.set_font("Helvetica", size=11)
    pdf.set_fill_color(255)
    with pdf.table(
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

    left,top = pdf.set_or_get("after attack table")

    # attack table explainer
    pdf.set_or_get(6.4, top+1, "before attack table explainer")
    pdf.attack_table_explainer()
    left,top = pdf.set_or_get("after attack table explainer")


    # space for notes check
    '''if enough space for notes and lines print notes and lines '''

    if 280 - top > 40:
        notes_output(pdf)

    pdf.perimiter_box() # must go last for z level

    pdf.add_page()

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD**",18)

    # player title right justified
    right_text = f"**Player:** _________________"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)
    
    pdf.hexagons()
    pdf.perimiter_box()

def record_back(pdf, persona, one_shot)->None:
    '''
    full page of equip and notes for one shot
    '''

    pdf.add_page()

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD** for {persona.Persona_Name}",18)

    # player title right justified
    right_text = f"**Player:** {persona.Player_Name}"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # to hex or not to hex
    if not one_shot:
        pdf.hexagons()
        pdf.sheet_footer(persona)
        pdf.perimiter_box()
        return

    # wate allowance is different for each family
    wate_allowance(pdf,persona)
    left,top = pdf.set_or_get("after wate allowance ? double")

    # 2 toy or not 2 toy
    if persona.FAMILY == "Alien" and persona.Society["Tools"] != "Flora or Fauna":
        toy_output(pdf,persona,lines=15)
    elif persona.FAMILY in ["Anthro","Robot"]:
        toy_output(pdf,persona,lines=15)
    left,top = pdf.set_or_get("after toy and lines")

    # notes
    notes_output(pdf)

    pdf.sheet_footer(persona)
    pdf.perimiter_box()

def campaign_sheet(pdf, persona, one_shot) -> None:
    '''
    outputs one side  TOYS and possible Notes. 
    other side is notes 
    '''

    ### side one front WA and TOYS?

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD** for {persona.Persona_Name}",18)

    # player title right justified
    right_text = f"**Player:** {persona.Player_Name}"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # needs to fill with TOYS or Notes
    wate_allowance(pdf,persona)
    left,top = pdf.set_or_get("after possible TOYS in backsheet")  

    # wate allowance is different for each family
    wate_allowance(pdf,persona)
    left,top = pdf.set_or_get("after wate allowance ? double")

    # 2 toy or not 2 toy full sheet
    if persona.FAMILY == "Alien" and persona.Society["Tools"] != "Flora or Fauna":
        toy_output(pdf,persona,lines=30)
    elif persona.FAMILY in ["Anthro","Robot"]:
        toy_output(pdf,persona,lines=30)
    left,top = pdf.set_or_get("after toy and lines")

    pdf.sheet_footer(persona)
    pdf.perimiter_box()

    ### side  two  back NOTES
    pdf.add_page()

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**PERSONA RECORD** for {persona.Persona_Name}",18)

    # player title right justified
    right_text = f"**Player:** {persona.Player_Name}"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # notes
    pdf.set_or_get(5.4,17.5, "before notes on campaign")
    notes_output(pdf)
    pdf.sheet_footer(persona)
    pdf.perimiter_box()

def robot_decay(persona, decay_table) -> None:
    '''
    pdf out a decay table for chosen robot
    '''    

    
    ###  PDF page prep
    pdf = PDF(orientation="P", unit="mm", format=(215.9, 279.4))
    pdf.set_margin(0)
    pdf.set_auto_page_break(False)
    pdf.add_page()

    # persona title left justified
    pdf.set_or_get(3.3, 5.7,"persona title")
    pdf.persona_title(f"**DEMOLITION TABLE** for {persona.Persona_Name}",18)

    # player title right justified
    right_text = f"**Player:** {persona.Player_Name}"
    pdf.set_or_get(216, 7.5, "player title")
    pdf.player_title(right_text,12)

    # put the decay table here
    pdf.set_or_get(5.8,17.5, "decay table line one")
    for decay_line in decay_table:
        pdf.markdown_robot_decay(decay_line, 10)

    pdf.sheet_footer(persona)
    pdf.perimiter_box() # must go last for z level    

    pdf.output(
        name="./Records/Bin/37bf560f9d0916a5467d7909.pdf",
        dest="F",
    )

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
        f"INT: {screenery.INT} MND: {screenery.MSTR} STR: {screenery.PSTR} HPS: {screenery.HPM} SOC: {screenery.SOC} WA: {screenery.WA}\n"
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
        f"MND: {bot_screen.MSTR} STR: {bot_screen.PSTR}({bot_screen.PSTR_Prime}) HPS: {bot_screen.HPM}\n"
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
        f"INT: {persona.INT} MND: {persona.MSTR} STR: {persona.PSTR} HPM: {persona.HPM} SOC: {persona.SOC} WA: {persona.WA}\n"
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
    



