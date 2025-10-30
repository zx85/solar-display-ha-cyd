# Functions to display text on the screen
# TODO: use anchors to denote position rather than repeated values

import gc
# import sys
from machine import Pin, SPI
from math import sin,cos,pi

# sys.path.append("/include")
# external things
from include.ili9341 import Display, color565
from include.xglcd_font import XglcdFont

# load the fonts
font = XglcdFont('fonts/FuturaNum21x39.c', 21, 39, 46)
font_uom = XglcdFont('fonts/Calibri12x14.c', 12, 14, 87)
font_num = XglcdFont('fonts/FuturaNum17x21.c', 17, 21, 46)
font_icon = XglcdFont('fonts/Emoji24x24.c',24, 24, 49)


# Arc drawing nicked from here https://www.scattergood.io/arc-drawing-algorithm/
def draw_arc(display, x, y, r1, r2, per,colour):
  gc.collect()
  if per>=100:
    fraction=1.0
  else:
    fraction=per/100
  start_angle=pi/2
  xs=x # cos(0) = 1
  ys=y+r1 # sin(0) = 0

#    display.draw_line(xs1,ys1,xs2,ys2,colour)

  max_angle=start_angle+(fraction*pi) # end at 270 degrees
  each_angle=start_angle # start at 90 degress
  step=pi/90
  while each_angle<max_angle:
    display.fill_polygon(4,
                        int(xs+(r1*cos(each_angle))),
                        int(ys+(r1*sin(each_angle))),
                        r2,colour,45+int(each_angle/pi*180))
    each_angle+=step


class SolarDisplay:
  def __init__(self):
    # Define the display doings
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0), rotation=270)
    self.display=display

  # Main function to do all the displaying
  def solar_data(self,solar_usage):
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

  def ip_address(self,ip):
    self.display.draw_text(80, 310, ip,font, color565(224, 224, 224), landscape=True)

  def clear(self):
    self.display.clear()

  def status_checking(self):
    self.display.fill_rectangle(238, 0, 2, 2, color565(192, 64, 64)) # checking
  
  def status_ok(self):
    self.display.fill_rectangle(238, 0, 2, 2, color565(0,0,0)) # done
  
  def status_invalid_data(self):
    self.display.fill_rectangle(238, 0, 2, 2, color565(0,192,192)) # done

  def status_failed(self):
    self.display.fill_rectangle(238, 0, 2, 2, color565(0,0,192)) # failed


  def solar_in(self,solar_usage):
    ############
    # solar_in #
    ############
    solar_in_max=5000
    solar_in_val=float(solar_usage["solar_in"])
    solar_in_per=int(solar_in_val/solar_in_max*100)

    if solar_in_val>1000:
      solar_in=str(solar_in_val/1000)[:4]
      solar_in_uom="kW[[now"
    else:
      solar_in=solar_usage["solar_in"].split(".")[0]
      solar_in_uom="W[[now"
    self.display.draw_text(65, 319, solar_in,font, color565(192, 255, 255), landscape=True) # solar_in value
    self.display.draw_vline(104,250,69,color565(64, 64, 64)) # solar_in line
    self.display.draw_text(105, 316, solar_in_uom,font_uom, color565(224, 224, 224), landscape=True) # solar_in uom

    if solar_in_val>1800:
      self.display.draw_text(32, 292, "1", font_icon, color565(192, 255, 255), landscape=True) # sun
    elif solar_in_val>1000:
      self.display.draw_text(32, 292, "2", font_icon, color565(64, 192, 192), landscape=True) # partial_cloud
    else:
      self.display.draw_text(32, 292, "3", font_icon, color565(128, 128, 128), landscape=True) # cloud

    draw_arc(self.display, 48, 250, 30, 5, solar_in_per,color565(64, 0, 0))

  def solar_today(self,solar_usage):
    ########################
    # solar_today - in kWh #
    ########################
    solar_today_max=30.0
    solar_today_per=int(float(solar_usage["solar_today"])/solar_today_max*100)
    solar_today_uom="kWh[[today"
    self.display.draw_text(180, 319, solar_usage["solar_today"][:4], font, color565(192, 255, 255), landscape=True) # solar_today value
    self.display.draw_vline(218,250,69,color565(64, 64, 64)) # solar_today line
    self.display.draw_text(220, 316, solar_today_uom,font_uom, color565(224, 224, 224), landscape=True) # solar_today uom
    self.display.draw_text(148, 293, "1", font_icon, color565(192, 255, 255), landscape=True) # sun

    draw_arc(self.display, 165, 250, 30, 5, solar_today_per,color565(64, 0, 0))

  def power_used(self,solar_usage):
    #####################
    # power_used - in W #
    #####################
    power_used_max=15000
    power_used_val=float(solar_usage["power_used"])
    power_used_per=int(power_used_val/power_used_max*100)
    if power_used_val>1000:
      power_used=str(power_used_val/1000)[:4]
      power_used_uom="kW[[now"
    else:
      power_used=solar_usage["power_used"].split(".")[0]
      power_used_uom="W[[now"

    self.display.draw_text(65, 228, power_used,font, color565(255, 255, 255), landscape=True) # power_used value
    self.display.draw_vline(104,159,69,color565(64, 64, 64)) # power_used line
    self.display.draw_text(105, 224, power_used_uom,font_uom, color565(224, 224, 224), landscape=True) # power_used uom
    self.display.draw_text(32, 206, "5", font_icon, color565(64, 64, 64), landscape=True) # plug

    draw_arc(self.display, 48, 162, 30, 5, power_used_per,color565(64, 0, 0))

  def export_today(self,solar_usage):
    #########################
    # export_today - in kWh #
    #########################
    export_today_max=25.0
    export_today_per=int(float(solar_usage["export_today"])/export_today_max*100)
    export_today_uom="kWh[[today"

    self.display.draw_text(180, 228, solar_usage["export_today"][:4],font, color565(192, 255, 192), landscape=True) # export_today value
    self.display.draw_vline(218,159,69,color565(64, 64, 64)) # export_today line
    self.display.draw_text(220, 224, export_today_uom,font_uom, color565(224, 224, 224), landscape=True)

    self.display.draw_text(148, 218, "6", font_icon, color565(192, 255, 192), landscape=True) # up
    self.display.draw_text(148, 194, "4", font_icon, color565(192, 192, 192), landscape=True) # zap

    draw_arc(self.display, 165, 158, 33, 5, export_today_per,color565(64, 0, 0))

  def grid_in(self,solar_usage):
    ##################
    # grid_in - in W #
    ##################
    grid_in_max=15000
    grid_out_max=5000
    grid_in_val=float(solar_usage["grid_in"])
    grid_in_per=int(abs(grid_in_val)/grid_in_max*100)
    if abs(grid_in_val)>1000:
      grid_in=str(abs(grid_in_val/1000))[:4]
      grid_in_uom="kW[[now"
    else:
      grid_in=str(abs(grid_in_val)).split(".")[0]
      grid_in_uom="W[[now"

    # colours for import / export
    if grid_in_val<0:
      grid_colour=color565(128, 128, 255) # pink
    elif grid_in_val>0:
      grid_colour=color565(128, 255, 128) # green
      # recalibrate for export
      grid_in_per=int(abs(grid_in_val)/grid_out_max*100)
    else:
      grid_colour=color565(255, 255, 255) # grey

    self.display.draw_text(65, 138, grid_in,font, grid_colour, landscape=True) # grid_in value
    self.display.draw_vline(104,69,69,color565(64, 64, 64)) # grid_in line
    self.display.draw_text(105, 132, grid_in_uom,font_uom, color565(224, 224, 224), landscape=True) # grid_in uom

    if grid_in_val<0:
      self.display.draw_text(32, 130, "7", font_icon, color565(64, 64, 192), landscape=True) # down
      self.display.draw_text(32, 106, "4", font_icon, color565(192, 192, 192), landscape=True) # zap
    elif grid_in_val>0:
      self.display.draw_text(32, 130, "6", font_icon, color565(64, 192, 64), landscape=True) # up
      self.display.draw_text(32, 106, "4", font_icon, color565(192, 192, 192), landscape=True) # zap
    else:
      self.display.draw_text(32, 116, "4", font_icon, color565(192, 192, 192), landscape=True) # zap

    draw_arc(self.display, 48, 74, 30, 5, grid_in_per,color565(64, 0, 0))

  def grid_in_today(self,solar_usage):
    ##########################
    # grid_in_today - in kWh #
    ##########################
    grid_in_today_max=40.0
    grid_in_today_per=int(float(solar_usage["grid_in_today"])/grid_in_today_max*100)
    grid_in_today_uom="kWh[[today"

    self.display.draw_text(180, 138, solar_usage["grid_in_today"][:4],font, color565(64, 64, 255), landscape=True)
    self.display.draw_vline(218,67,69,color565(64, 64, 64)) # grid_in_today line
    self.display.draw_text(220, 132, grid_in_today_uom,font_uom, color565(224, 224, 224), landscape=True)

    self.display.draw_text(148, 124, "7", font_icon, color565(64, 64, 192), landscape=True) # down
    self.display.draw_text(148, 100, "4", font_icon, color565(192, 192, 192), landscape=True) # zap

    draw_arc(self.display, 165, 68, 32, 6, grid_in_today_per,color565(64, 0, 0))
  
  def battery(self,solar_usage):
    ##################
    # battery - in % #
    ##################
    battery_per_val=float(solar_usage["battery_per"])
    # note: % symbol is actually / in the font bytecode
    self.display.draw_text(98, 52, f"{solar_usage["battery_per"].split(".")[0]}/",font_num, color565(255, 230, 230), landscape=True)
    self.display.fill_rectangle(12, 25, 6, 16, color565(255, 192, 192)) # battery top
    self.display.fill_rectangle(18, 18, 60, 30, color565(255, 192, 192)) # battery outline
    self.display.fill_rectangle(21, 22, 50-int(battery_per_val/2), 22, color565(0, 0, 0)) # battery drain
    if battery_per_val<solar_usage["prev_battery_int"]: # battery goes down
      self.display.fill_polygon(3,87,35,8,color565(64, 64, 192),0)
    elif battery_per_val>solar_usage["prev_battery_int"]: # battery goes up
      self.display.fill_polygon(3,91,33,8,color565(64, 192, 64),180)
    else: # battery stays the same
      self.display.fill_rectangle(86,24,6,20,color565(192, 192, 192))

  def timestamp(self,solar_usage):
    ###################
    # timestamp hh:mm #
    ###################
    self.display.draw_text(1, 319, f"{solar_usage["timestamp"].split("T")[1][:5]}", font_num, color565(64, 64, 64), landscape=True) # time

  def cur_rate(self,solar_usage):
    #######################################
    # current agile rate - sent in pounds #
    #######################################
    root_x=12
    root_y=135
    rate=float(solar_usage['cur_rate'])*100
    if rate>=15:
       rate_col=color565(64, 64, 192)
    elif rate>=10:
      rate_col=color565(64, 192, 192)
    elif rate>0:
      rate_col=color565(64, 192, 64)
    else:
      rate_col=color565(192, 64, 64)
    rate_string=f'{rate:.2f}?'.replace("-","@")
    print(f"rate_string is {rate_string}")
    self.display.draw_text(root_x, root_y, rate_string, font_num, rate_col, landscape=True) 

  def presence(self,solar_usage):
    # presence #
    for index, initial in enumerate('jBCL'):
      if initial in solar_usage['presence']:
        status_colour=color565(128, 192, 128)
      else:
        status_colour=color565(16, 16, 16)
      self.display.draw_text(125+index*29, 40,chr(59+index), font_num, status_colour, landscape=True) # person
      self.display.draw_circle(134+index*29, 31, 12, status_colour)
