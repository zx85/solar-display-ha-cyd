# Functions to display text on the screen
# TODO: use anchors to denote position rather than repeated values

import gc

# import sys
from machine import Pin, SPI
from math import sin, cos, pi

# sys.path.append("/include")
# external things
from include.ili9341 import Display, color565
from include.xglcd_font import XglcdFont

# load the fonts
font = XglcdFont("fonts/FuturaNum21x39.c", 21, 39, 46)
font_uom = XglcdFont("fonts/Calibri12x14.c", 12, 14, 87)
font_num = XglcdFont("fonts/FuturaNum17x21.c", 17, 21, 46)
font_icon = XglcdFont("fonts/Emoji24x24.c", 24, 24, 49)

bin_scale = 0.1


# Arc drawing nicked from here https://www.scattergood.io/arc-drawing-algorithm/
def draw_arc(display, x, y, r1, r2, per, colour):
    gc.collect()
    if per >= 100:
        fraction = 1.0
    else:
        fraction = per / 100
    start_angle = pi / 2
    xs = x  # cos(0) = 1
    ys = y + r1  # sin(0) = 0

    #    display.draw_line(xs1,ys1,xs2,ys2,colour)

    max_angle = start_angle + (fraction * pi)  # end at 270 degrees
    each_angle = start_angle  # start at 90 degress
    step = pi / 90
    while each_angle < max_angle:
        display.fill_polygon(
            4,
            int(xs + (r1 * cos(each_angle))),
            int(ys + (r1 * sin(each_angle))),
            r2,
            colour,
            45 + int(each_angle / pi * 180),
        )
        each_angle += step


class SolarDisplay:
    def __init__(self):
        # Define the display doings
        spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
        display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0), rotation=270)
        self.display = display

    # Main function to do all the displaying
    def solar_data(self, solar_usage):
        self.display.clear()
        self.solar_in(solar_usage)
        self.solar_today(solar_usage)
        self.power_used(solar_usage)
        self.export_today(solar_usage)
        self.grid_in(solar_usage)
        self.grid_in_today(solar_usage)
        self.timestamp(solar_usage)
        self.battery(solar_usage)
        self.presence(solar_usage)
        self.cur_rate(solar_usage)
        if solar_usage.get("bins"):
            self.bins(solar_usage)

    def ip_address(self, ip):
        self.display.draw_text(
            80, 310, ip, font, color565(224, 224, 224), landscape=True
        )

    def clear(self):
        self.display.clear()
        gc.collect()

    def status_checking(self):
        self.display.fill_rectangle(238, 0, 2, 2, color565(192, 64, 64))  # checking

    def status_ok(self):
        self.display.fill_rectangle(238, 0, 2, 2, color565(0, 0, 0))  # done

    def status_invalid_data(self):
        self.display.fill_rectangle(238, 0, 2, 2, color565(0, 192, 192))  # done

    def status_failed(self):
        self.display.fill_rectangle(238, 0, 2, 2, color565(0, 0, 192))  # failed

    def solar_in(self, solar_usage):
        ############
        # solar_in #
        ############
        root_x = 65
        root_y = 319
        solar_in_max = 5000
        solar_in_val = solar_usage["solar_in"]
        solar_in_per = int(solar_in_val / solar_in_max * 100)

        if solar_in_val > 1000:
            solar_in_str = str(solar_in_val / 1000)[:4]
            solar_in_uom = "kWxnow"
        else:
            solar_in_str = f"{solar_in_val:.0f}"
            solar_in_uom = "Wxnow"
        self.display.draw_text(
            root_x, root_y, solar_in_str, font, color565(192, 255, 255), landscape=True
        )  # solar_in value
        self.display.draw_vline(
            root_x + 39, root_y - 69, 69, color565(64, 64, 64)
        )  # solar_in line
        self.display.draw_text(
            root_x + 40,
            root_y - 3,
            solar_in_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )  # solar_in uom

        if solar_in_val > 1800:
            self.display.draw_text(
                root_x - 33,
                root_y - 27,
                "1",
                font_icon,
                color565(192, 255, 255),
                landscape=True,
            )  # sun
        elif solar_in_val > 1000:
            self.display.draw_text(
                root_x - 33,
                root_y - 27,
                "2",
                font_icon,
                color565(64, 192, 192),
                landscape=True,
            )  # partial_cloud
        else:
            self.display.draw_text(
                root_x - 33,
                root_y - 27,
                "3",
                font_icon,
                color565(128, 128, 128),
                landscape=True,
            )  # cloud

        draw_arc(
            self.display,
            root_x - 17,
            root_y - 69,
            30,
            5,
            solar_in_per,
            color565(64, 0, 0),
        )

    def solar_today(self, solar_usage):
        ########################
        # solar_today - in kWh #
        ########################
        root_x = 180
        root_y = 319
        solar_today_max = 30.0
        solar_today_per = solar_usage["solar_today"] / solar_today_max * 100
        solar_today_str = f'{solar_usage["solar_today"]}'[:4]
        solar_today_uom = "kWhxtodey"
        self.display.draw_text(
            root_x,
            root_y,
            solar_today_str,
            font,
            color565(192, 255, 255),
            landscape=True,
        )  # solar_today value
        self.display.draw_vline(
            root_x + 38, root_y - 69, 69, color565(64, 64, 64)
        )  # solar_today line
        self.display.draw_text(
            root_x + 40,
            root_y - 3,
            solar_today_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )  # solar_today uom
        self.display.draw_text(
            root_x - 32,
            root_y - 26,
            "1",
            font_icon,
            color565(192, 255, 255),
            landscape=True,
        )  # sun

        draw_arc(
            self.display,
            root_x - 15,
            root_y - 69,
            30,
            5,
            solar_today_per,
            color565(64, 0, 0),
        )

    def power_used(self, solar_usage):
        #####################
        # power_used - in W #
        #####################
        root_x = 65
        root_y = 228
        power_used_max = 15000
        power_used_val = solar_usage["power_used"]
        power_used_per = int(power_used_val / power_used_max * 100)
        if power_used_val > 1000:
            power_used_str = f"{str(power_used_val/1000)}"[:4]
            power_used_uom = "kWxnow"
        else:
            power_used_str = f"{power_used_val:.0f}"
            power_used_uom = "Wxnow"

        self.display.draw_text(
            root_x,
            root_y,
            power_used_str,
            font,
            color565(255, 255, 255),
            landscape=True,
        )  # power_used value
        self.display.draw_vline(
            root_x + 39, root_y - 69, 69, color565(64, 64, 64)
        )  # power_used line
        self.display.draw_text(
            root_x + 40,
            root_y - 4,
            power_used_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )  # power_used uom
        self.display.draw_text(
            root_x - 33,
            root_y - 22,
            "5",
            font_icon,
            color565(64, 64, 64),
            landscape=True,
        )  # plug

        # draw_arc(self.display, root_x-17, root_y-64, 30, 5, power_used_per, color565(64, 0, 0))

    def export_today(self, solar_usage):
        #########################
        # export_today - in kWh #
        #########################
        root_x = 180
        root_y = int(
            228 * (1 if solar_usage.get("bins") else 1 - bin_scale)
        )  # scale for bins
        export_today_max = 25.0
        export_today_val = solar_usage["export_today"]
        # Prevent negative values
        if export_today_val < 0:
            export_today_val = 0
        export_today_str = f"{export_today_val}"[:4]
        export_today_per = int(export_today_val / export_today_max * 100)
        export_today_uom = "kWhxtodey"

        self.display.draw_text(
            root_x,
            root_y,
            export_today_str,
            font,
            color565(192, 255, 192),
            landscape=True,
        )  # export_today value
        self.display.draw_vline(
            root_x + 38, root_y - 69, 69, color565(64, 64, 64)
        )  # export_today line
        self.display.draw_text(
            root_x + 40,
            root_y - 4,
            export_today_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )

        self.display.draw_text(
            root_x - 32,
            root_y - 10,
            "6",
            font_icon,
            color565(192, 255, 192),
            landscape=True,
        )  # up
        self.display.draw_text(
            root_x - 32,
            root_y - 34,
            "4",
            font_icon,
            color565(192, 192, 192),
            landscape=True,
        )  # zap

        draw_arc(
            self.display,
            root_x - 15,
            root_y - 69,
            33,
            5,
            export_today_per,
            color565(64, 0, 0),
        )

    def grid_in(self, solar_usage):
        ##################
        # grid_in - in W #
        ##################
        root_x = 65
        root_y = 138
        grid_in_max = 15000
        grid_out_max = 5000
        grid_in_val = solar_usage["grid_in"]
        grid_in_per = int(abs(grid_in_val) / grid_in_max * 100)
        if abs(grid_in_val) > 1000:
            grid_in_str = f"{abs(grid_in_val/1000)}"[:4]
            grid_in_uom = "kWxnow"
        else:
            grid_in_str = f"{abs(grid_in_val)}".split(".")[0]
            grid_in_uom = "Wxnow"

        # colours for import / export
        if grid_in_val < 0:
            grid_colour = color565(128, 128, 255)  # pink
        elif grid_in_val > 0:
            grid_colour = color565(128, 255, 128)  # green
            # recalibrate for export
            grid_in_per = int(abs(grid_in_val) / grid_out_max * 100)
        else:
            grid_colour = color565(255, 255, 255)  # grey

        self.display.draw_text(
            root_x, root_y, grid_in_str, font, grid_colour, landscape=True
        )  # grid_in value
        self.display.draw_vline(
            root_x + 39, root_y - 69, 69, color565(64, 64, 64)
        )  # grid_in line
        self.display.draw_text(
            root_x + 40,
            root_y - 6,
            grid_in_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )  # grid_in uom

        if grid_in_val < 0:
            self.display.draw_text(
                root_x - 33, 130, "7", font_icon, color565(64, 64, 192), landscape=True
            )  # down
            y_offset = 32
        elif grid_in_val > 0:
            self.display.draw_text(
                root_x - 33, 130, "6", font_icon, color565(64, 192, 64), landscape=True
            )  # up
            y_offset = 32
        else:
            # no arrow
            y_offset = 22
        self.display.draw_text(
            root_x - 33,
            root_y - y_offset,
            "4",
            font_icon,
            color565(192, 192, 192),
            landscape=True,
        )  # zap
        # draw_arc(self.display, root_x-17, root_y-64, 30, 5, grid_in_per, color565(64, 0, 0))

    def grid_in_today(self, solar_usage):
        ##########################
        # grid_in_today - in kWh #
        ##########################
        root_x = 180
        root_y = int(
            138 * (1 if solar_usage.get("bins") else 1 - (bin_scale * 3))
        )  # scale for no bin icon
        grid_in_today_max = 40.0
        grid_in_today_val = solar_usage["grid_in_today"]
        # Prevent negative values
        if grid_in_today_val < 0:
            grid_in_today_val = 0
        grid_in_today_str = f"{grid_in_today_val}"[:4]
        grid_in_today_per = int(grid_in_today_val / grid_in_today_max * 100)
        grid_in_today_uom = "kWhxtodey"

        self.display.draw_text(
            root_x,
            root_y,
            grid_in_today_str,
            font,
            color565(64, 64, 255),
            landscape=True,
        )
        self.display.draw_vline(
            root_x + 38, root_y - 69, 69, color565(64, 64, 64)
        )  # grid_in_today line
        self.display.draw_text(
            root_x + 40,
            root_y - 6,
            grid_in_today_uom,
            font_uom,
            color565(224, 224, 224),
            landscape=True,
        )

        self.display.draw_text(
            root_x - 32,
            root_y - 14,
            "7",
            font_icon,
            color565(64, 64, 192),
            landscape=True,
        )  # down
        self.display.draw_text(
            root_x - 32,
            root_y - 38,
            "4",
            font_icon,
            color565(192, 192, 192),
            landscape=True,
        )  # zap

        draw_arc(
            self.display,
            root_x - 15,
            root_y - 69,
            32,
            6,
            grid_in_today_per,
            color565(64, 0, 0),
        )

    def battery(self, solar_usage):
        ##################
        # battery - in % #
        ##################
        root_x = 98
        root_y = 52
        battery_per_val = solar_usage["battery_per"]
        battery_per_str = f"{battery_per_val}".split(".")[0]
        # note: % symbol is actually / in the font bytecode
        self.display.draw_text(
            root_x,
            root_y,
            f"{battery_per_str}/",
            font_num,
            color565(255, 230, 230),
            landscape=True,
        )
        self.display.fill_rectangle(
            root_x - 86, root_y - 27, 6, 16, color565(255, 192, 192)
        )  # battery top
        self.display.fill_rectangle(
            root_x - 80, root_y - 34, 60, 30, color565(255, 192, 192)
        )  # battery outline
        self.display.fill_rectangle(
            root_x - 77,
            root_y - 30,
            50 - int(battery_per_val / 2),
            22,
            color565(0, 0, 0),
        )  # battery drain
        if battery_per_val < solar_usage["prev_battery_int"]:  # battery goes down
            self.display.fill_polygon(
                root_x - 95, root_y + 35, 35, 8, color565(64, 64, 192), 0
            )
        elif battery_per_val > solar_usage["prev_battery_int"]:  # battery goes up
            self.display.fill_polygon(
                root_x - 95, root_y + 39, 33, 8, color565(64, 192, 64), 180
            )
        else:  # battery stays the same
            self.display.fill_rectangle(
                root_x - 12, root_y - 28, 6, 20, color565(192, 192, 192)
            )
        # charge and discharge modes
        if solar_usage["solis_discharging"] == "on":
            self.display.fill_polygon(
                root_x - 95, root_y + 5, 33, 8, color565(64, 0, 0), 0
            )
            self.display.fill_rectangle(
                root_x - 64, root_y - 21, 30, 4, color565(64, 0, 0)
            )
        if solar_usage["solis_charging"] == "on":
            self.display.fill_polygon(
                root_x - 95, root_y - 17, 33, 8, color565(64, 0, 0), 180
            )
            self.display.fill_rectangle(
                root_x - 64, root_y - 21, 30, 4, color565(64, 0, 0)
            )

    def timestamp(self, solar_usage):
        ###################
        # timestamp hh:mm #
        ###################
        root_x = 6
        root_y = 319
        self.display.draw_text(
            root_x,
            root_y,
            f"{solar_usage["timestamp"].split("T")[1][:5]}",
            font_num,
            color565(64, 64, 64),
            landscape=True,
        )  # time

    def rate_lookup(self, in_rate):
        lookup = {
            "0": "X",
            "1": "Y",
            "2": "Z",
            "3": "[",
            "4": "\\",
            "5": "]",
            "6": "^",
            "7": "_",
            "8": "`",
            "9": "a",
            ".": "b",
            "-": "j",
            "p": "p",
        }
        out_rate = ""
        for char in in_rate:
            out_rate += lookup.get(char)
        return out_rate

    def cur_rate(self, solar_usage):
        #######################################
        # current agile rate - sent in pounds #
        #######################################
        root_x = 12
        root_y = 126
        rate = solar_usage["cur_rate"] * 100
        if rate >= 15:
            rate_col = color565(64, 64, 192)
        elif rate >= 10:
            rate_col = color565(64, 192, 192)
        elif rate > 0:
            rate_col = color565(64, 192, 64)
        else:
            rate_col = color565(192, 64, 64)
        # power up special colour
        if solar_usage["power_up"] == "on":
            rate_col = color565(192, 64, 192)

        rate_str_raw = f"{rate:.2f}p"
        rate_str = self.rate_lookup(rate_str_raw)
        print(f"rate_str_raw ({rate_str_raw}) -> rate_str: {rate_str}")

        self.display.draw_text(
            root_x, root_y, rate_str, font_uom, rate_col, landscape=True
        )
        # power up rectangle
        if solar_usage["power_up"] == "on":
            self.display.draw_rectangle(
                root_x - 3, root_y - 70, 25, 75, rate_col
            )  # outline

    def presence(self, solar_usage):
        # presence #
        root_x = 6
        root_y = 259
        for index, initial in enumerate("jBCL"):
            if initial in solar_usage["presence"]:
                status_colour = color565(128, 192, 128)
            else:
                status_colour = color565(16, 16, 16)
            self.display.draw_text(
                root_x,
                root_y - index * 33,
                chr(59 + index),
                font_num,
                status_colour,
                landscape=True,
            )  # person
            self.display.draw_circle(
                root_x + 8, root_y - 8 - index * 33, 12, status_colour
            )

    def bins(self, solar_usage):
        #####################
        # power_used - in W #
        #####################
        root_x = 125
        root_y = 17
        gc.collect()
        bins = solar_usage.get("bins")
        if len(bins) == 2:  # 2 chars per bin
            print(f"1 bins: {bins}")
            self.display.draw_image(
                f"images/wheelie-bin-{bins}-48x33.raw", root_x + 58, root_y, 48, 33
            )
        elif len(bins) == 4:  # only space for 2 bins
            print(f"2 bins: {bins}")
            self.display.draw_image(
                f"images/wheelie-bin-{bins[0:2]}-48x33.raw", root_x, root_y, 48, 33
            )
            self.display.draw_image(
                f"images/wheelie-bin-{bins[2:4]}-48x33.raw", root_x + 58, root_y, 48, 33
            )
        else:
            print(f"Unsupported bin string (not 2 or 4 characters): {bins}")
