import math
import os
import time
import webbrowser

from fpdf import FPDF

import please
import mutations
import vocation
import table


################################################
#
# classes for pdf creation
#
################################################


class PDF(FPDF):
    def perimiter_box(self):
        # topped off  box for title space
        # self.rect(self.x, self.y, (LETTER_WIDTH-2*self.x), (LETTER_HEIGHT-2*self.y), "D")

        width = 216
        height = 279
        self.set_draw_color(0, 0, 0)
        self.set_line_width(1)

        self.x = 5
        self.y = 13
        # LETTER_WIDTH = 216
        # LETTER_HEIGHT = 279

        self.rect(self.x, self.y, (self.epw - 2 * self.x), (self.eph - 20), "D")

    def cross_hair(self, radius):  # helps line up things during composition of pdf
        LETTER_WIDTH = 216
        LETTER_HEIGHT = 279
        self.radius = radius

        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.1)
        self.circle(
            (LETTER_WIDTH / 2 - self.radius / 2),
            (LETTER_HEIGHT / 2 - self.radius / 2),
            self.radius,
            "D",
        )
        self.line(LETTER_WIDTH / 2, 0, LETTER_WIDTH / 2, LETTER_HEIGHT)
        self.line(0, LETTER_HEIGHT / 2, LETTER_WIDTH, LETTER_HEIGHT / 2)

    def locutus(self):
        """
        makes aarrow at x and y
        """
        x = self.get_x()
        y = self.get_y()

        self.set_draw_color(256, 1, 1)
        self.set_fill_color(1, 256, 1)
        self.set_line_width(0.2)
        point_one = (x, y)
        point_two = (x - 2, y - 1)
        point_three = (x - 2, y + 1)

        self.polygon([point_one, point_two, point_three], fill=True)

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
                content, styling = datum.split(":")
                alignment = styling[0]
                accenture = styling[1] if styling[1] != "N" else ""

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

    def title_line(self, object):
        self.object = object

        # print out PERSONA NAME BIG and LEFT justified
        self.set_font("helvetica", size=18)
        self.set_xy(3, 5.8)
        self.cell(
            w=0,
            markdown=True,
            txt=f"**PERSONA RECORD** for {self.object.Persona_Name}",
            ln=0,
        )

        # print out PLAYER NAME Small and RIGHT justified
        self.set_font("helvetica", size=12)
        blob = f"**Player:** {self.object.Player_Name}"
        txt_width = 210 - self.get_string_width(blob, markdown=True)
        self.set_xy(txt_width, 7.8)
        self.cell(
            w=0,
            markdown=True,
            txt=blob,
            ln=0,
        )

    def attributes_lines(self, object):
        self.object = object
        x_left = 5
        x_right = 213

        ## attribute acronym set up
        data = [
            [],
            [
                "AWE:CB",
                "CHA:CB",
                "CON:CB",
                "DEX:CB",
                "INT:CB",
                "MSTR:CB",
                "PSTR:CB",
                "SOC:CB",
                "HPM:CB",
                "HPS:CB",
            ],
        ]

        # attribute acronyms output
        self.set_font("Helvetica", size=12)
        self.table_vomit(data, x_left, x_right, 12, 1.1, 0)

        ## attribute values set up
        data[1][-1] = "HPM:CB"  # swap out HPS title for HPS on attribute value line

        working_data = [
            getattr(self.object, attribby.split(":")[0]) for attribby in data[1]
        ]
        data[1] = [f"{str(x)}:CI" for x in working_data]

        ## attribute value line ouptut
        self.set_font("Helvetica", size=13)
        self.table_vomit(data, x_left, x_right, 17, 1.1, 0)

        ## attribute descriptor set up
        self.set_font("Helvetica", size=7)

        data = [
            [],
            [
                "Awareness:CN",
                "Charisma:CN",
                "Constitution:CN",
                "Dexterity:CN",
                "Intelligence:CN",
                "Psionics:CN",
                "Strength:CN",
                "Privilege:CN",
                "Max Hit Points:CN",
                "Hit Points Now:CN",
            ],
        ]

        ## attribute description line
        self.set_font("Helvetica", size=7)
        self.table_vomit(data, 6, 212, 22, 1.1, 0)

        ## HPS BOX
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.25)

        self.x = 193.5
        self.y = 31
        # LETTER_WIDTH = 216
        # LETTER_HEIGHT = 279

        self.rect(self.x, self.y, 16, self.y + 21.3, "D")

    def description_line(self, object):
        self.object = object

        self.set_font("Helvetica", size=12)
        line_height = self.font_size * 2

        if self.object.FAMILY == "Anthro":
            blob = f"**DESCRIPTION:** {self.object.Age} year-old {self.object.Anthro_Sub_Type.lower()} {self.object.Vocation.lower()}."

        elif self.object.FAMILY == "Alien":
            blob = f"**DESCRIPTION:** {self.object.Quick_Description}"

        elif self.object.FAMILY == "Robot":
            blob = f"**DESCRIPTION:** {self.object.Description}"

        else:
            print("ERROR: No description for this persona")

        self.set_xy(8, 33)
        self.cell(w=0, h=line_height, markdown=True, txt=blob, ln=True)

    def combat_table_titler(self, object, *args):
        self.object = object
        self.table_title = args[0]

        exps_next = list(table.vocation_exps_levels[self.object.Vocation].keys())[
            self.object.Level - 1
        ].stop  # pulls next exps goal from range based on level

        # which blob to use

        if self.table_title == "Vocation":
            blob = f"**COMBAT INFO** for {self.object.Vocation} **Level** {self.object.Level} **EXPS** ({self.object.EXPS}/{exps_next})"

        elif self.table_title == "Alien":
            blob = f"**COMBAT INFO** for {self.object.Alien_Type} **Level** {self.object.Level} **EXPS** ({self.object.EXPS}/{exps_next})"

        elif self.table_title == "Robot":
            blob = f"**COMBAT INFO** for {self.object.Robot_Type} **Level** {self.object.Level} **EXPS** ({self.object.EXPS}/{exps_next})"

        # Combat Info Title
        self.set_font("Helvetica", size=12)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        self.set_xy(8, self.get_y() + 2)
        line_width = self.get_string_width(blob, markdown=True) + 5
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        line_height = self.font_size * 1.5  # restore list line height
        self.set_y(self.get_y() + 1)

    def combat_table_explainer(self):
        self.set_font("Helvetica", size=9)
        line_height = self.font_size * 1.2
        self.set_xy(8, self.get_y() + 0.5)

        self.multi_cell(
            w=0,
            align="L",
            h=line_height,
            markdown=True,
            txt=f"**Raw:** Add to Unskilled Attack Rolls  **Skilled:** Add to Skilled Attack Rolls **Max:**  Maximum Attack Roll **Force:** Add to damage roll\n**Strike:** fist, sword, club  **Fling:** bow, spear, spit **Shoot:** gun, lazer, fission **Sotto/Flotto:** = Shoot **Grenade:** = Fling, no Force",
        )

        return

    def ar_move_show(self):
        self.set_font("Helvetica", size=12)
        line_height = self.font_size * 1.4
        self.set_xy(8, self.get_y() + 0.0)

        movement = (
            f"{self.object.Move} h/u" if self.object.FAMILY != "Alien" else "See below"
        )
        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=f"**ARMOUR RATING (AR):** {self.object.AR}      **MOVE:** {movement}",
            ln=1,
        )

        return

    def combat_table_pd_effer(self, object, *args):
        self.object = object

        self.table_title = args[0]

        # which table to use
        if self.table_title == "Vocation":
            combat_table = vocation_combat_tabler(self.object, "return", "all")

        elif self.table_title == "Alien":
            combat_table = alien_combat_tabler(self.object, "return", "all")

        elif self.table_title == "Robot":
            combat_table = robot_combat_tabler(self.object, "return", "all")

        # calculate the combat table
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
        if ABP > 0:
            data.append(
                [
                    "Strike:LB",
                    f"{ABNP}:CI",
                    f"{ABP}:CI",
                    f"{AMR}:CI",
                    f"{ADB}:CI",
                ]
            )

        if BBP > 0:
            data.append(
                [
                    "Fling:LB",
                    f"{BBNP}:CI",
                    f"{BBP}:CI",
                    f"{BMR}:CI",
                    f"{BDB}:CI",
                ]
            )

        if CBP > 0:
            data.append(
                [
                    "Shoot:LB",
                    f"{CBNP}:CI",
                    f"{CBP}:CI",
                    f"{CMR}:CI",
                    f"{CDB}:CI",
                ]
            )

        # table_vomit the ABCs of combat table
        align_proficiency = self.get_y()
        self.table_vomit(data, 9, 105, self.get_y(), 1.5, 0.25)

        # table proficiencies
        if type(APROF) == int:
            prof_slot = "___________ " if APROF not in [4, 5] else "______ "
            APROF = f"{APROF} {prof_slot*APROF}"

        if type(BPROF) == int:
            prof_slot = "___________ " if BPROF not in [4, 5] else "______ "
            BPROF = f"{BPROF} {prof_slot*BPROF}"

        if type(CPROF) == int:
            prof_slot = "___________ " if CPROF not in [4, 5] else "______ "
            CPROF = f"{CPROF} {prof_slot*CPROF}"

        data = [["Skilled Weapons:LB"]]

        if ABP > 0:
            data.append([f"{APROF}:LI"])

        if BBP > 0:
            data.append([f"{BPROF}:LI"])

        if CBP > 0:
            data.append([f"{CPROF}:LI"])

        # table_vomit the proficiencies for ABC
        self.table_vomit(data, 106, 192, align_proficiency, 1.5, 0.25)

        # explainer for the combat table acronyms
        if self.table_title == "Vocation":
            self.combat_table_explainer()
            self.ar_move_show()

        elif self.table_title == "Alien" and self.object.Vocation == "Alien":
            self.combat_table_explainer()
            self.ar_move_show()

        elif self.table_title == "Robot" and self.object.Vocation == "Robot":
            self.combat_table_explainer()
            self.ar_move_show()

    def alien_move(self, object):
        self.object = object
        move_type = ["Move_Land", "Move_Air", "Move_Water"]
        blob = ""

        for terrain in move_type:
            move_rate = getattr(self.object, terrain)
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

    def task_info(self, object):
        self.object = object
        exps_next = list(table.vocation_exps_levels[self.object.Vocation].keys())[
            self.object.Level - 1
        ].stop  # pulls next exps goal from range based on level

        # Task Info Title
        self.set_font("Helvetica", size=12)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        self.set_xy(8, self.get_y() + 2)
        blob = f"**TASK INFO** for {self.object.Vocation} **Level** {self.object.Level} **EXPS** ({self.object.EXPS}/{exps_next})"
        line_width = self.get_string_width(blob, markdown=True) + 5
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.25  # restore list line height

        ### vocation GIFTS
        task_top_gifts = self.get_y() + 1.5
        self.set_xy(8, task_top_gifts)
        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=f"**GIFTS**",
            ln=1,
        )

        gift_list = vocation.update_gifts(self.object)
        for x, gift in enumerate(gift_list):
            self.set_x(8)
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"{x+1}) {gift}",
                ln=1,
            )

        task_bottom_gifts = self.get_y()

        ### vocation INTERESTS
        self.set_xy(38, task_top_gifts)
        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=f"**INTERESTS**",
            ln=1,
        )

        collated_interests = please.collate_this(self.object.Interests)
        for x, interest in enumerate(collated_interests):
            self.set_x(38)
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"{x+1}) {interest}",
                ln=1,
            )

        task_bottom_interests = self.get_y()

        skill_bottom = (
            task_bottom_interests
            if task_bottom_interests > task_bottom_gifts
            else task_bottom_gifts
        )

        ### vocation  SKILLS
        self.set_xy(78, task_top_gifts)

        # skills_y_start = task_bottom_gifts
        # self.set_xy(8, skills_y_start)
        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=f"**SKILLS**",
            ln=1,
        )

        collated_skills = please.collate_this(object.Skills)

        ### stacking the skills by 3
        skill_x = 78
        skill_top = self.get_y()
        for x, skill in enumerate(collated_skills):
            if (x + 1) in [4, 7]:
                skill_x = skill_x + 34
                self.set_y(skill_top)
            self.set_x(skill_x)
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"{x+1}) {skill}",
                ln=1,
            )
            if (x + 1) == 3:
                skill_bottom = self.get_y()

        ### reset y to lowest
        # self.set_y(skill_bottom + 1.5)

        self.set_xy(8, skill_bottom + 1.5)

        if self.object.Vocation == "Spie":
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"{self.object.Spie_Fu}",
                ln=1,
            )

        if object.Vocation == "Nothing":
            if object.EXPS > object.Vocay_Aspiration_EXPS:
                achievation = "Achieved!"
            else:
                fraction = int((object.EXPS / object.Vocay_Aspiration_EXPS) * 100)
                achievation = f"{fraction}% achieved"

            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"Aspiration: {object.Vocay_Aspiration} Objective: {achievation}",
                ln=1,
            )

    def biologic_info(self, object):
        self.object = object

        # BIOLOGIC Info Title
        self.set_font("Helvetica", size=12)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        # self.set_xy(8, self.get_y() + 2)
        self.set_x(8)
        blob = f"**BIOLOGIC INFO** for {self.object.FAMILY} {self.object.Anthro_Type}  {self.object.Anthro_Sub_Type}"
        line_width = self.get_string_width(blob)
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        self.set_font("Helvetica", size=10)
        self.set_xy(8, self.get_y() + 1)
        blob = f"**Family** {self.object.FAMILY} **Type:** {self.object.Anthro_Type} **Sub Type:** {self.object.Anthro_Sub_Type} **Age:** {self.object.Age} years **Hite:** {self.object.Hite} cms **Wate:** {self.object.Wate} kgs"
        self.cell(w=0, markdown=True, txt=blob, ln=True, fill=False)

        # print out Mutations
        self.set_xy(8, self.get_y())
        line_height = self.font_size * 1.5
        if len(self.object.Mutations) == 0:
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"**Mutations:** None",
            )

        else:
            self.set_xy(8, self.get_y())

            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"**Mutations:**",
                ln=1,
            )

            self.set_font("Helvetica", size=9)
            line_height = self.font_size * 1.25

            all_mutations = mutations.make_pivot_table()

            for name in sorted(self.object.Mutations.keys()):
                working_mutation = all_mutations[name](self.object)
                header, details, param = working_mutation.return_details(
                    working_mutation.__class__
                )

                self.set_x(8)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"**{header}**",
                    # ln=1,
                )
                self.set_xy(8, self.get_y() + line_height)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"{details}",
                    # ln=1,
                )
                self.set_xy(8, self.get_y() + line_height)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"{param}",
                    # ln=1,
                )

                self.set_xy(8, self.get_y() + 1.4 * line_height)

        if self.object.RP and self.object.Vocation in [
            voc for voc in table.vocations_gifts_pivot
        ]:
            # RP FUN
            self.set_xy(8, self.get_y() + 5)
            self.set_font("Helvetica", size=10)
            line_height = self.font_size * 1.4
            blob = f"**RP FUN** for {self.object.Persona_Name}"
            line_width = 0  # full width
            self.cell(
                w=line_width,
                h=line_height,
                markdown=True,
                txt=blob,
                ln=1,
                fill=False,
                border=False,
            )

            for fun in self.object.RP_Fun:

                self.set_x(8)
                self.cell(
                    w=line_width,
                    h=line_height,
                    markdown=True,
                    txt=fun,
                    ln=1,
                    fill=False,
                    border=False,
                )

    def alien_biologic_info(self, object):
        self.object = object

        ### ALIEN BIOLOGIC Info Title
        self.set_font("Helvetica", size=12)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        self.set_xy(8, self.get_y() + 2)
        blob = f"**XENOLOGIC INFO** for {self.object.FAMILY} **SPECIES:** {self.object.Alien_Type}"
        line_width = self.get_string_width(blob)
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        # specific person age hite and wate
        self.set_xy(8, self.get_y())
        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.4
        blob = f"**Specific Alien:** {self.object.Persona_Name} **Age:** {self.object.Age} {self.object.Alien_Age_Suffix} old. **Hite:** {self.object.Size} **Wate:** {self.object.Wate} {self.object.Wate_Suffix}."
        line_width = 0  # full width
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        ### assign the y for Description
        top_desc_and_life_y = self.get_y()
        left_desc_xeno_x = 8
        left_life_society_x = 98

        ### desc detailed description

        ### need to make list because multi_cell does not work as expected
        desc_parts = [
            f"Head: {object.Head.split(' (')[0]}{object.Head_Adorn}",
            f"Body: {object.Body.split(' (')[0]}{object.Body_Adorn}",
            f"Arms: {object.Arms.split(' (')[0]}{object.Arms_Adorn}",
            f"Legs: {object.Legs.split(' (')[0]}",
        ]

        self.set_xy(left_desc_xeno_x, top_desc_and_life_y)
        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.3
        blob = f"**Description:**"
        line_width = 0  # full width
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        for part in desc_parts:
            self.set_x(left_desc_xeno_x)
            self.cell(
                w=line_width,
                h=line_height,
                markdown=True,
                txt=part,
                ln=1,
                fill=False,
                border=False,
            )

        ### life Life Span information
        self.set_xy(left_life_society_x, top_desc_and_life_y)
        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.3
        blob = f"**Life Span:**"
        line_width = 0  # full width
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        for stage in self.object.Life_Cycle:
            self.set_x(left_life_society_x)
            self.cell(
                w=line_width,
                h=line_height,
                markdown=True,
                txt=stage,
                ln=1,
                fill=False,
                border=False,
            )

        ### xeno Xenologic information
        top_of_xeno = self.get_y()
        self.set_xy(left_desc_xeno_x, self.get_y())
        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.3
        blob = f"**Xenobiology**"
        line_width = 0  # full width
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        for xeno in self.object.Biology:
            self.set_x(left_desc_xeno_x)
            self.cell(
                w=line_width,
                h=line_height,
                markdown=True,
                txt=xeno,
                ln=1,
                fill=False,
                border=False,
            )

        bottom_of_xeno = self.get_y()

        # Society information
        self.set_xy(left_life_society_x, top_of_xeno)
        self.set_font("Helvetica", size=10)
        line_height = self.font_size * 1.3
        blob = f"**Society** of {self.object.Alien_Type}"
        line_width = 0  # full width
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        for techno in self.object.Society:
            self.set_x(left_life_society_x)
            self.cell(
                w=line_width,
                h=line_height,
                markdown=True,
                txt=techno,
                ln=1,
                fill=False,
                border=False,
            )

        bottom_of_society = self.get_y()

        # print out Mutations aka powers
        top_mutations = (
            bottom_of_society if bottom_of_society > bottom_of_xeno else bottom_of_xeno
        )

        self.set_xy(8, top_mutations)
        line_height = self.font_size * 1.4
        if len(self.object.Mutations) == 0:
            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"**Powers:** None",
            )

        else:
            self.set_xy(8, self.get_y())

            self.cell(
                w=0,
                h=line_height,
                markdown=True,
                txt=f"**Powers:**",
                ln=1,
            )

            self.set_font("Helvetica", size=9)
            line_height = self.font_size * 1.25

            all_mutations = mutations.make_pivot_table()

            for name in sorted(self.object.Mutations.keys()):
                working_mutation = all_mutations[name](self.object)
                header, details, param = working_mutation.return_details(
                    working_mutation.__class__
                )

                self.set_x(8)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"**{header}**",
                    # ln=1,
                )
                self.set_xy(8, self.get_y() + line_height)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"{details}",
                    # ln=1,
                )
                self.set_xy(8, self.get_y() + line_height)
                self.cell(
                    w=0,
                    h=line_height,
                    markdown=True,
                    txt=f"{param}",
                    # ln=1,
                )

                self.set_xy(8, self.get_y() + 1.4 * line_height)

    def note_lines(self):
        self.x = self.get_x()
        self.y = self.get_y()
        lines = 275 - 5 - self.y
        if lines < 10:
            return

        # More Info Title
        self.set_font("Helvetica", size=12)
        self.set_line_width(0.1)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        self.set_xy(8, self.get_y() + line_height)
        blob = f"**MORE INFO**"
        line_width = self.get_string_width(blob)
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        for more_y in range(int(lines / 7)):
            self.line(
                8, self.y + more_y * line_height, 210, self.y + more_y * line_height
            )

    def wate_allowance(self, object):
        self.object = object
        self.set_font("Helvetica", size=12)
        self.set_line_width(0.1)
        self.set_fill_color(200)
        self.set_draw_color(150)
        line_height = self.font_size * 1.6
        self.set_xy(8, self.get_y() + 2)
        blob = f"**TOYS**"
        line_width = self.get_string_width(blob)
        self.cell(
            w=line_width,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=True,
            border=True,
        )

        self.set_font("Helvetica", size=12)
        line_height = self.font_size * 1.6
        self.set_xy(40, 15)

        blob = f"**Carry Capacity:** up to {self.object.WA*1.5} kg. **No penalty:** <{self.object.WA/4} kg. **Lift Only:** {self.object.WA*2.5} kg."

        self.cell(
            w=0,
            h=line_height,
            markdown=True,
            txt=blob,
            ln=1,
            fill=False,
            border=False,
        )

        self.line(8, self.y, 210, self.y)  # hack to fill an ugly gap

        for more_y in range(int(15)):
            self.line(
                8, self.y + more_y * line_height, 103, self.y + more_y * line_height
            )
            self.line(
                107, self.y + more_y * line_height, 208, self.y + more_y * line_height
            )

        self.set_xy(10, 120)

    def id_data(self, object):
        self.object = object
        self.set_font("Helvetica", size=7)
        line_height = self.font_size * 1.6
        self.set_xy(8, 273)
        self.object.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())
        blob = f" **Updated:** {self.object.Date_Updated} **Created:** {self.object.Date_Created} **File Name:** {self.object.File_Name}"

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

    def combat_tabler(object, *args):
        if args[0] not in ["output", "Output", "return", "Return"]:
            print(f"{args[0]} is not a valid option for combat_tabler")
            quit()

        elif args[0] in ["return", "Return"] and args[1] not in ["All", "all"]:
            print(f"{args[1]} is not a valid option for combat_tabler")
            quit()

        # rebuild args
        if args[0] in ["return", "Return"]:
            arg_one = args[0]
            arg_two = args[1]

        else:
            arg_one = args[0]
            arg_two = "wangafangabobanga"

        # anthro, vocation = vocation and tasks
        # alien, vocation = vocation and tasks, and alien
        # robot, vocaiton = vocation and tasks, and robot
        # alien, alien = alien
        # robot, robot = robot

        vocation_yes = object.Vocation in [x for x in table.vocation_level_bonus.keys()]

        if object.FAMILY == "Anthro":
            combat_table = vocation_combat_tabler(object, arg_one, arg_two)
            return

        if object.FAMILY == "Alien" and vocation_yes:
            combat_table = vocation_combat_tabler(object, arg_one, arg_two)
            combat_table = alien_combat_tabler(object, arg_one, arg_two)
            pass

        if object.FAMILY == "Alien" and vocation_yes:
            # vocation_combat_tabler(object, *args)
            # robot_combat_tabler(object, *args)
            # done and leave
            pass

        if object.FAMILY == "Alien" and not vocation_yes:
            # alien_combat_tabler(object, *args)
            # done and leave
            pass

        if object.FAMILY == "Alien" and not vocation_yes:
            # robot_combat_tabler(object, *args)
            # done and leave
            pass

        if (
            object.Vocation in [x for x in table.vocation_level_bonus.keys()]
            and object.FAMILY != "Robot"
        ):
            combat_table = vocation_combat_tabler(object, args)

        if object.FAMILY == "Alien":
            combat_table = alien_combat_tabler(object, args)

        if object.FAMILY == "Robot":
            combat_table = robot_combat_tabler(object, args)

        return combat_table


##############################################
#
# functions to support outputs
#
##############################################


def pdf_opener(object: dict) -> None:
    """
    opens PDF of choice in the browser of choice
    """
    target_pdf = f"{object.File_Name}.pdf"
    if object.FAMILY == "Toy":
        directory_to_use = "file:///C:/Users/mobil/OneDrive/Documents/Persona%20Record/EXP_Game_Tools/Records/Toys/"

    else:
        directory_to_use = (
            "file:///C:/Users/mobil/OneDrive/Documents/Persona%20Record/EXP_Game_Tools/Records/Referee/"
            if object.RP
            else "file:///C:/Users/mobil/OneDrive/Documents/Persona%20Record/EXP_Game_Tools/Records/Players/"
        )

    webbrowser.get().open_new(f"{directory_to_use}{target_pdf}")

    return


def vocation_combat_tabler(calc, *args):
    # args test
    if args[0] not in ["output", "Output", "return", "Return"]:
        print(f"{args[0]} is not a valid option")
        quit()

    elif args[0] in ["return", "Return"] and args[1] not in ["All", "all"]:
        print(f"{args[1]} is not a valid option")
        quit()

    # collect needed data
    awe = calc.AWE
    dex = calc.DEX
    intel = calc.INT
    pstr = calc.PSTR
    family = calc.FAMILY
    vocation = calc.Vocation
    level = calc.Level
    prof_level = (
        calc.Level - 1 if calc.Level < 11 else 9
    )  # safety to between 0 and 9 for prof list
    if family == "Alien":  # safety for alien with vocation and Move dummy value
        calc.Move = dex

    # print ("AWE", awe, "DEX", dex, "INT", intel, "PSTR", pstr, "VOC", vocation, "LVL", level)

    combat_table = {
        "A": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "B": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "C": {"BP": 0, "BNP": 0, "MR": 0, "DB": 0, "PROF": 0},
        "TITLE": f"{vocation} LVL {level}",
        "ARMOVE": f"Armour Rating (AR): {calc.AR}      Move: {calc.Move} h/u",
    }

    # TYPE A THRUSTING AND STRIKING WEAPONS
    ABP = math.ceil((1.5 * awe) + (2 * dex) + (1.5 * intel) + (5 * pstr))
    ABP = ABP + table.vocation_level_bonus[vocation]["A"] * level
    ABNP = math.ceil(ABP * table.vocation_non_proficient[vocation]["A"] / 100)
    AMR = 625 + ABP
    ADB = math.ceil(pstr / 2)
    APROF = table.vocation_proficiencies[vocation]["A"][prof_level]

    # assign (ABP, ABNP, AMR, ADB)
    combat_table["A"]["BP"] = ABP
    combat_table["A"]["BNP"] = ABNP
    combat_table["A"]["MR"] = AMR
    combat_table["A"]["ADB"] = ADB

    # TYPE B THROWING AND MISSILE WEAPONS
    BBP = awe + (4 * dex) + intel + (2 * pstr)
    BBP = BBP + table.vocation_level_bonus[vocation]["B"] * level
    BBNP = math.ceil(BBP * (table.vocation_non_proficient[vocation]["B"] / 100))
    BMR = 650 + BBP
    BDB = math.ceil(pstr / 4)
    BPROF = table.vocation_proficiencies[vocation]["B"][prof_level]

    # print(BBP, BBNP, BMR, BDB)
    combat_table["B"]["BP"] = BBP
    combat_table["B"]["BNP"] = BBNP
    combat_table["B"]["MR"] = BMR
    combat_table["B"]["BDB"] = BDB

    # TYPE C POWERED WEAPONS
    CBP = awe + (9 * dex) + intel + pstr
    CBP = CBP + table.vocation_level_bonus[vocation]["C"] * level
    CBNP = math.ceil(CBP * (table.vocation_non_proficient[vocation]["C"] / 100))
    CMR = 675 + CBP
    CDB = 0
    CPROF = table.vocation_proficiencies[vocation]["C"][prof_level]

    # (CBP, CBNP, CMR, CDB)
    combat_table["C"]["BP"] = CBP
    combat_table["C"]["BNP"] = CBNP
    combat_table["C"]["MR"] = CMR
    combat_table["C"]["CDB"] = CDB

    # work through proficiency sentence
    if APROF == 42 and vocation == "Mercenary":
        APROF = "All weapons."
        BPROF = "All weapons."
        CPROF = "All weapons."

    elif APROF == 42 and vocation == "Nothing":
        APROF = " "
        BPROF = "One single proficiency."
        CPROF = " "

    combat_table["A"]["PROF"] = APROF
    combat_table["B"]["PROF"] = BPROF
    combat_table["C"]["PROF"] = CPROF

    # where to go with the combat_table
    if args[0] in [
        "output",
        "Output",
    ]:
        output_combat_tabler(calc, combat_table)
    elif args[0] in ["return", "Return"]:
        return combat_table

    return combat_table


def alien_combat_tabler(calc, *args):
    # args test
    if args[0] not in ["output", "Output", "return", "Return"]:
        print(f"{args[0]} is not a valid option")
        quit()

    elif args[0] in ["return", "Return"] and args[1] not in ["All", "all"]:
        print(f"{args[1]} is not a valid option")
        quit()

    # collect needed data
    dex = calc.DEX
    intel = calc.INT
    pstr = calc.PSTR
    level = calc.Level
    attack_type = calc.Attack_Type
    attacks = calc.Attacks
    attack_desc = calc.Attack_Desc
    damage = f"{calc.Damage}"

    combat_table = {
        "A": {
            "BP": 0,
            "BNP": 0,
            "MR": 0,
            "ADB": 0,
            "PROF": f"Natural - {attacks} {attack_desc} for {damage} HPS.",
        },
        "B": {
            "BP": 0,
            "BNP": 0,
            "MR": 0,
            "BDB": 0,
            "PROF": f"Natural - {attacks} {attack_desc} for {damage} HPS.",
        },
        "C": {
            "BP": 0,
            "BNP": 0,
            "MR": 0,
            "CDB": 0,
            "PROF": f"Natural - {attacks} {attack_desc} for {damage} HPS.",
        },
        "TITLE": f"{calc.Alien_Type} LVL {level}",
        "ARMOVE": f"Armour Rating (AR): {calc.AR}     Move: See below",
    }

    # TYPE A NON-POWERED STRIKING WEAPONS
    if attack_type == "Type A (contact)":
        ABP = ABNP = 10 * (pstr + level)
        AMR = 700 + ABP
        ADB = level
        PROF = "APROF"
        combat_table["A"]["BP"] = ABP
        combat_table["A"]["BNP"] = ABNP
        combat_table["A"]["MR"] = AMR
        combat_table["A"]["ADB"] = ADB
        # combat_table["A"]["PROF"] = APROF

    # TYPE B NON-POWERED MISSILE WEAPONS
    if attack_type == "Type B (ranged)":
        BBP = BBNP = 10 * (dex + level)
        BMR = 700 + BBP
        BDB = level
        PROF = "BPROF"

        # print(BBP, BBNP, BMR, BDB)
        combat_table["B"]["BP"] = BBP
        combat_table["B"]["BNP"] = BBNP
        combat_table["B"]["MR"] = BMR
        combat_table["B"]["BDB"] = BDB
        # combat_table["B"]["PROF"] = BPROF

    # TYPE C POWERED MISSILE WEAPONS
    if attack_type == "Type C (power ranged)":
        CBP = CBNP = 10 * (intel + level)
        CMR = 700 + CBP
        CDB = level
        PROF = "CPROF"

        # (CBP, CBNP, CMR, CDB)
        combat_table["C"]["BP"] = CBP
        combat_table["C"]["BNP"] = CBNP
        combat_table["C"]["MR"] = CMR
        combat_table["C"]["CDB"] = CDB
        # combat_table["C"]["PROF"] = CPROF

    combat_table[
        "ARMOVE"
    ] = f"{table.numbers_2_words[attacks].capitalize()} {table.attack_type_words[PROF]} attack {attack_desc}. {damage} total damage.\n\nArmour Rating (AR): {calc.AR}     Move: See below"

    # where to go with the combat_table
    if args[0] in [
        "output",
        "Output",
    ]:
        output_combat_tabler(calc, combat_table)
    elif args[0] == ["return", "Return"]:
        return combat_table

    return combat_table


def robot_combat_tabler(calc, *args):
    # args test
    if args[0] not in ["output", "Output", "return", "Return"]:
        print(f"{args[0]} is not a valid option")
        quit()

    elif args[0] in ["return", "Return"] and args[1] not in ["All", "all"]:
        print(f"{args[1]} is not a valid option")
        quit()

    dex = calc.DEX
    intel = calc.INT
    pstr = calc.PSTR
    awe = calc.AWE
    lvl = calc.Level
    pstr_prime = calc.PSTR_Prime
    dex_prime = calc.DEX_Prime
    intel_prime = calc.INT_Prime

    combat_table = {
        "A": {"BP": 0, "BNP": 0, "MR": 0, "ADB": 0, "PROF": "Baked in attacks only."},
        "B": {"BP": 0, "BNP": 0, "MR": 0, "BDB": 0, "PROF": "Baked in attacks only."},
        "C": {"BP": 0, "BNP": 0, "MR": 0, "CDB": 0, "PROF": "Baked in attacks only."},
        "TITLE": f"{calc.Robot_Type} LVL {lvl}",
        "ARMOVE": f"Armour Rating (AR): {calc.AR}     Move: {calc.Move}",
    }

    # TYPE A THRUSTING AND STRIKING WEAPONS
    ABP = (5 * dex) + (5 * intel) + (pstr_prime * pstr) + (lvl * pstr)
    ABNP = 0
    AMR = "---"
    ADB = pstr
    # print(ABP, ABNP, AMR, ADB)
    combat_table["A"]["BP"] = ABP
    combat_table["A"]["BNP"] = ABNP
    combat_table["A"]["MR"] = AMR
    combat_table["A"]["ADB"] = ADB

    # TYPE B THROWING AND MISSILE WEAPONS
    BBP = (5 * awe) + (5 * pstr) + (dex_prime * dex) + (lvl * dex)
    BBNP = 0
    BMR = "---"
    BDB = math.ceil(pstr / 2)
    # print(BBP, BBNP, BMR, BDB)
    combat_table["B"]["BP"] = BBP
    combat_table["B"]["BNP"] = BBNP
    combat_table["B"]["MR"] = BMR
    combat_table["B"]["ADB"] = BDB

    # TYPE C POWERED WEAPONS
    CBP = (5 * awe) + (5 * dex) + (intel_prime * intel) + (lvl * intel)
    CBNP = 0
    CMR = "---"
    CDB = 0
    # (CBP, CBNP, CMR, CDB)
    combat_table["C"]["BP"] = CBP
    combat_table["C"]["BNP"] = CBNP
    combat_table["C"]["MR"] = CMR
    combat_table["C"]["ADB"] = CDB

    # where to go with the combat_table
    if args[0] in [
        "output",
        "Output",
    ]:
        output_combat_tabler(calc, combat_table)
    elif args[0] == ["return", "Return"]:
        return combat_table

    return combat_table


def output_combat_tabler(object, combat_table):
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

    if object.FAMILY != "Alien":
        print(f'{combat_table["ARMOVE"]}')

    return


#####################################
# ANTHRO output to screen
#####################################


def anthro_review(object):
    please.clear_console()
    print(
        f"\n\nANTHRO PERSONA RECORD\n"
        f"Persona: {object.Persona_Name} \t\t\tPlayer: {object.Player_Name} \tCreated: {object.Date_Created}\n"
        f"AWE: {object.AWE} CHA: {object.CHA} CON: {object.CON} DEX: {object.DEX} "
        f"INT: {object.INT} MSTR: {object.MSTR} PSTR: {object.PSTR} HPS: {object.HPM} SOC: {object.SOC} WA: {object.WA}\n"
        f"Family: {object.FAMILY} Type: {object.Anthro_Type} SubType: {object.Anthro_Sub_Type}\n"
        f"Age: {object.Age} years Hite: {object.Hite} cms Wate: {object.Wate} kgs\n"
        f"Vocation: {object.Vocation} Level: {object.Level} EXPS: {object.EXPS}"
    )

    # show the combat table
    vocation_combat_tabler(object, "output")

    # anthro Gifts
    gift_list = vocation.update_gifts(object)
    print(f"\n{object.Vocation} GIFTS: ")
    for x, gift in enumerate(gift_list):
        print(f"{x + 1}) {gift}")

    # anthro  Interest list
    print(f"\n{object.Vocation} INTERESTS: ")
    collated_interests = please.collate_this(object.Interests)

    for x, interest in enumerate(collated_interests):
        print(f"{x + 1}) {interest}")

    # anthro  Skills
    print(f"\n{object.Vocation} SKILLS: ")
    collated_skills = please.collate_this(object.Skills)
    for x, skill in enumerate(collated_skills):
        print(f"{x + 1}) {skill}")

    # special cases for nothing and spie

    if object.Vocation == "Spie":
        print(f"{object.Spie_Fu}")

    if object.Vocation == "Nothing":
        if object.EXPS > object.Vocay_Aspiration_EXPS:
            achievation = "Achieved!"
        else:
            fraction = int((object.EXPS / object.Vocay_Aspiration_EXPS) * 100)
            achievation = f"{fraction}% achieved"

        print(f"Aspiration: {object.Vocay_Aspiration} Objective: {achievation}")

    # print out Mutations
    print("\nMUTATIONS", end=" ")

    if len(object.Mutations) == 0:
        print("None")

    else:
        all_mutations = mutations.make_pivot_table()

        for name, perm in sorted(object.Mutations.items()):
            working_mutation = all_mutations[name](object)
            working_mutation.post_details(working_mutation.__class__)

    if object.RP:
        print("\nReferee Persona ROLE-PLAYING CUES")
        for fun in object.RP_Fun:
            print(f"{fun}")

    return

#####################################
# Bespoke Back pager PDF
#####################################

def backpage_creator(object):
    print ("at backpage_creator")
    please.show_me_your_dict(object)
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    pdf.add_page()
    pdf.perimiter_box()
    pdf.title_line(object)
    pdf.note_lines()

    pdf.add_page()
    pdf.title_line(object)
    pdf.perimiter_box()
    pdf.note_lines()

    sub_directory = "Referee" if object.RP else "Players"
    pdf_name = f"./Records/{sub_directory}/{object.File_Name}.BACKPAGER.pdf"
    pdf.output(
        name=pdf_name,
        dest="F",
    )
    print(f"\n***PDF stored at ./Records/{sub_directory}/{object.File_Name}.pdf")
    return



#####################################
# ANTHRO output to PDF
#####################################


def anthro_pdf_creator(object):
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    pdf.add_page()
    pdf.perimiter_box()
    pdf.title_line(object)
    pdf.attributes_lines(object)
    pdf.description_line(object)
    pdf.combat_table_titler(object, "Vocation")
    pdf.combat_table_pd_effer(object, "Vocation")

    pdf.task_info(object)
    pdf.biologic_info(object)
    pdf.note_lines()

    pdf.add_page()
    pdf.title_line(object)
    pdf.perimiter_box()
    pdf.wate_allowance(object)
    pdf.note_lines()
    pdf.id_data(object)

    sub_directory = "Referee" if object.RP else "Players"
    pdf_name = f"./Records/{sub_directory}/{object.File_Name}.pdf"
    pdf.output(
        name=pdf_name,
        dest="F",
    )
    print(f"\n***PDF stored at ./Records/{sub_directory}/{object.File_Name}.pdf")
    return


#####################################
# ALIEN output to screen
#####################################


def alien_review(alien):
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
        f"Family: {alien.FAMILY} Species: {alien.Alien_Type}\n"
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
    print(f"\nNATURAL POWERS of {alien.Alien_Type}")

    if len(alien.Mutations) == 0:
        print("None")

    else:
        all_mutations = mutations.make_pivot_table()

        for name, perm in sorted(alien.Mutations.items()):
            working_mutation = all_mutations[name](alien)
            working_mutation.post_details(working_mutation.__class__)

    print(f"\nBIOLOGY of {alien.Alien_Type}")
    for bio_line in alien.Biology:
        print(f"{bio_line}")
    print("")
    for bio_line in alien.Life_Cycle:
        print(f"{bio_line}")

    print(f"\nSOCIETY of {alien.Alien_Type}")
    for soc_line in alien.Society:
        print(f"{soc_line}")

    return


#####################################
# AlIEN output to PDF
#####################################


def alien_pdf_creator(alien):
    ### create the pdf
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    ### add the page and create the box
    pdf.add_page()
    pdf.perimiter_box()
    pdf.title_line(alien)

    ### output the persona
    pdf.attributes_lines(alien)
    pdf.description_line(alien)

    pdf.combat_table_titler(alien, "Alien")
    pdf.combat_table_pd_effer(alien, "Alien")

    if alien.Vocation != "Alien":
        pdf.combat_table_titler(alien, "Vocation")
        pdf.combat_table_pd_effer(alien, "Vocation")

    pdf.alien_move(alien)

    if alien.Vocation != "Alien":
        pdf.task_info(alien)

    pdf.alien_biologic_info(alien)

    pdf.note_lines()

    pdf.add_page()
    pdf.title_line(alien)
    pdf.perimiter_box()
    pdf.wate_allowance(alien)
    pdf.note_lines()
    pdf.id_data(alien)

    sub_directory = "Referee" if alien.RP else "Players"
    pdf_name = f"./Records/{sub_directory}/{alien.File_Name}.pdf"

    pdf.output(
        name=pdf_name,
        dest="F",
    )
    print(f"\n***PDF stored at /Records/{sub_directory}/{alien.File_Name}.pdf")
    return


#####################################
# ROBOT output to screen
#####################################


def robot_review(robot: dict) -> None:
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
    pdf = PDF(orientation="P", unit="mm", format=(216, 279))
    pdf.set_margin(0)  # set margins to 0

    pdf.add_page()
    pdf.perimiter_box()
    pdf.title_line(robot)
    pdf.attributes_lines(robot)
    pdf.description_line(robot)
    if robot.Vocation != "Robot":
        pdf.combat_table_titler(robot, "Vocation")
        pdf.combat_table_pd_effer(robot, "Vocation")
    pdf.combat_table_titler(robot, "Robot")
    pdf.combat_table_pd_effer(robot, "Robot")
    if robot.Vocation != "Robot":
        pdf.task_info(robot)

    pdf.add_page()
    pdf.title_line(robot)
    pdf.perimiter_box()
    pdf.wate_allowance(robot)
    pdf.note_lines()
    pdf.id_data(robot)

    sub_directory = "Referee" if robot.RP else "Players"
    pdf_name = f"./Records/{sub_directory}/{robot.File_Name}.pdf"

    pdf.output(
        name=pdf_name,
        dest="F",
    )
    print(f"\n***PDF stored at ./Records/{sub_directory}/{robot.File_Name}.pdf")
    return
