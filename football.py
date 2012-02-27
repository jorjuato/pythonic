#!/usr/bin/env python

"""
 * Copyright (C) 2005 Varun Hiremath and Kumar Appaiah.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * @author Varun Hiremath and Kumar Appaiah
 * @version 0.8
"""

import Gnuplot
#from Numeric import *
from random import *
from math import sin, cos, sqrt
import math
import time
import copy
import StringIO

#PASS_ANGLES = [[1, 2, 3, 2, 1, 4, 1, 2, 3, 2], [2, 4, 1, 4, 1, 3, 2, 1, 2, 1]]
PASS_ANGLES = [[1, 2, 3, 2, 1, 4, 1, 2, 3, 2], [2, 2, 1, 7, 4, 3, 2, 2, 2, 3]]
#PLAYER_SPEEDS = [[0.9, 0.95, 0.98, 0, 1, 0, 0.94, 0.9, 1, 0.98, 0], \
#          [1.5, 2, 1.5, 2, 1.5, 2, 1.5, 2, 1.5, 2, 2]]
PLAYER_SPEEDS = [[0.98, 0.98, 0.98, 0.99, 1, 0.9, 0.94, 0.9, 1, 0.98, 1], \
                 [1.02, 1.05, 0.95, 0.99, 1, 0.9, 0.94, 0.9, 1, 0.98, 0.97]]
KICKING_SPEEDS = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
HISTORY_LENGTH = 50
GAME_TIME = 500

TEAM_NAMES = {1: "Pinks",
              2: "Blues"}

## STATISTICS

def signum(n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    return 0


class Team:
    def __init__(self):
        self.formation=(0,0,0)
        self.defenders=[]
        self.forwards=[]
        self.midfielders=[]
        self.goalkeeper=[]
        self.player_positions=[]
        self.starting_positions=[]
        self.goals=0
        self.pass_angle_ratings=[]
        self.player_speeds=[]
        self.kicking_speeds=[]
        self.history = []
        self.fouls = 0
        self.possession_time = 0
        self.corners=0
        self.goal_attempts=0
        self.goal_attempts_on_target = 0


class Football:
    def __init__(self,length,breadth):

        self.game = False
        self.toss = 0
        self.length=length
        self.breadth=breadth

        self.player_walk=self.length/150
        self.player_run=self.length/80
        self.player_run_fast=self.length/60
        self.player_height=self.length/100
        self.player_gap=self.length/5
        self.player_range=self.length/15
       
        self.ball=[0,0,0]
        self.ball_goal_hit=self.length/10
        self.ball_speed_fast=self.length/12
        self.ball_speed_slow=self.length/16
        self.ball_free = False
        self.ball_path = []
        self.ball_pass={'grd_pass':1,'air_pass':2,'goal_hit':3}
        
        self.team_possessing_ball = 0
        self.player_possessing_ball=[0,0]
        self.player_withball_pos=[0,0]
        self.ball_passed_to=[0,0]
        self.goal_thickness=self.length/100
        self.goal_width=self.breadth/12
        
        self.team=[]
        self.team.extend([0,Team(),Team()])
        self.ball_history = []
        self.last_kicked_pos = [0, 0]
        self.penalty=False
        self.Foul=False
        self.pos_sign = 1
        self.side_changed=False
        self.half_time_details = False

    def make_team(self,team_no,formation, angle_ratings, player_speeds, kicking_speeds):
                
        if(team_no==1):
            side=-1
        elif(team_no==2):
            side=1
            
        if(formation==(4,4,2)):
        
            self.team[team_no].formation=formation
            self.team[team_no].goalkeeper=[side*9*self.length/19,0]
            self.team[team_no].defenders.extend(
                [[side*self.length/4,-self.breadth*3.0/10],
                 [side*self.length/3,-self.breadth*1.0/10],
                 [side*self.length/3,self.breadth*1.0/10],
                 [side*self.length/4,self.breadth*3.0/10]])

            self.team[team_no].midfielders.extend(
                [[side*self.length/12,-self.breadth*4.0/10],
                 [side*self.length/6,-self.breadth*1.0/10],
                 [side*self.length/6,self.breadth*1.0/10],
                 [side*self.length/12,self.breadth*4.0/10]])

            self.team[team_no].forwards.extend(
                [[side*self.length/80,0],
                 [side*self.length/30,self.breadth/10.0]])
            
        elif(formation==(4,3,3)):
        
            self.team[team_no].formation=formation
            self.team[team_no].goalkeeper=[side*9*self.length/19,0]
            self.team[team_no].defenders.extend(
                [[side*self.length/4,-self.breadth*3.0/10],
                 [side*self.length/3,-self.breadth*1.0/10],
                 [side*self.length/3,self.breadth*1.0/10],
                 [side*self.length/4,self.breadth*3.0/10]])

            self.team[team_no].midfielders.extend(
                [[side*self.length/12,-self.breadth/3],
                 [side*self.length/6,0],
                 [side*self.length/12,self.breadth/3]])
            self.team[team_no].forwards.extend(
                [[side*self.length/75,0],
                 [side*self.length/30,self.breadth/10.0],
                 [side*self.length/30,-self.breadth/10.0]])

        
        self.team[team_no].pass_angle_ratings = angle_ratings
        self.team[team_no].player_speeds = player_speeds
        self.team[team_no].kicking_speeds = kicking_speeds
        self.team[team_no].starting_positions=[]
        self.team[team_no].starting_positions.extend(copy.deepcopy(self.team[team_no].forwards))
        self.team[team_no].starting_positions.extend(copy.deepcopy(self.team[team_no].midfielders))
        self.team[team_no].starting_positions.extend(copy.deepcopy(self.team[team_no].defenders))
        self.team[team_no].starting_positions.append(copy.deepcopy(self.team[team_no].goalkeeper))
        ##print self.team[team_no].starting_positions
        ##raw_input()
            
    def get_player_positions(self):
         for i in range(1,3):
             self.team[i].player_positions=[]
             self.team[i].player_positions.extend(self.team[i].forwards)
             self.team[i].player_positions.extend(self.team[i].midfielders)
             self.team[i].player_positions.extend(self.team[i].defenders)
             self.team[i].player_positions.append(self.team[i].goalkeeper)


    def start_game(self):
        #print "in start game"
        if self.toss == 0:
            if random()<0.5:
                self.toss=1
            else:
                self.toss=2

        self.team[self.toss].forwards[0]=[0,0]
        self.player_withball_pos=[0,0]
        self.player_possessing_ball=[self.toss,0]
        rn=randint(self.team[self.toss].formation[2],9-self.team[self.toss].formation[0])
        
        if rn<self.team[self.toss].formation[2]:
            pos2=self.team[self.toss].forwards[rn]
        elif rn<6:
            pos2=self.team[self.toss].midfielders[rn-self.team[self.toss].formation[2]]
        else:
            pos2=self.team[self.toss].defenders[rn-6]
        self.team_possessing_ball=self.toss            
        self.move_ball([0,0],pos2,self.ball_pass['grd_pass'])
        #     self.ball_passed_to=[self.toss,rn]
        self.ball_free = True
        self.game=True


    def move_a_forward_player(self,T_no,sign,BC):
        for pln in range(self.team[T_no].formation[2]):
            updiv=-self.breadth/2 + 2*(pln+1)*self.breadth/(2*self.team[T_no].formation[2]+1)
            ldiv=-self.breadth/2 + (2*pln+1)*self.breadth/(2*self.team[T_no].formation[2]+1)
            if self.player_possessing_ball!=[T_no,pln]: 
                if self.ball_in_player_range(self.team[T_no].forwards[pln]) and not self.Foul:
                    if self.ball_free or self.team_possessing_ball!=T_no:
                        self.move_player(T_no,pln,self.ball)
                        
                else:
                    if sign*self.team[T_no].forwards[pln][0]< sign*BC:
                        self.team[T_no].forwards[pln][0]+=sign*self.player_run*self.team[T_no].player_speeds[pln]
                        if self.team[T_no].forwards[pln][1]>updiv:
                            self.team[T_no].forwards[pln][1]-=self.player_run*self.team[T_no].player_speeds[pln]
                        elif self.team[T_no].forwards[pln][1]<ldiv:
                            self.team[T_no].forwards[pln][1]+=self.player_run*self.team[T_no].player_speeds[pln]
                        
                            
                    else:
                        self.team[T_no].forwards[pln]=self.move_player_random(self.team[T_no].forwards[pln], T_no, pln)

    def move_forward_players(self,T_no):
        if T_no==1:
            sign=1
            Tnpb=2
        else:
            sign=-1
            Tnpb=1
        if self.team_possessing_ball==T_no:
    
            if self.player_possessing_ball[1]>5:
                own_pl=min(8*self.length/20,sign*(self.player_withball_pos[0]+sign*self.player_gap*2))
                own_pl*=sign
            elif self.player_possessing_ball[1]>=self.team[T_no].formation[2]:
                own_pl=min(8*self.length/20,sign*(self.player_withball_pos[0]+3/2*sign*self.player_gap))
                own_pl*=sign
            else:
                own_pl=min(8*self.length/20,sign*self.player_withball_pos[0])
                own_pl*=sign

            self.move_a_forward_player(T_no,sign,own_pl)    
                   
        elif self.team_possessing_ball!=T_no:
            if self.player_possessing_ball[1]>5:
                opponent_pos=min(8*self.length/20-self.player_gap*2,-sign*self.player_withball_pos[0])
                opponent_pos*=-sign
            elif self.player_possessing_ball[1]>=self.team[T_no].formation[2]:
                opponent_pos=min(8*self.length/20-self.player_gap*2,-sign*self.player_withball_pos[0])
                opponent_pos*=-sign
            else:
                opponent_pos=max(8*self.length/20-self.player_gap*2,-sign*self.player_withball_pos[0])
                opponent_pos*=-sign
                   
            self.move_a_forward_player(T_no,-sign,opponent_pos)    


    def move_a_midfielder(self,T_no,sign,BC):
        offset = self.team[T_no].formation[2]
        for pln in range(self.team[T_no].formation[1]):

            updiv=-self.breadth/2 + 2*(pln+1)*self.breadth/(2*self.team[T_no].formation[1]+1)
            ldiv=-self.breadth/2 + (2*pln+1)*self.breadth/(2*self.team[T_no].formation[1]+1)
            
            if self.player_possessing_ball!=[T_no,pln+self.team[T_no].formation[2]]:
                
                if self.ball_in_player_range(self.team[T_no].midfielders[pln]) and not self.Foul:
                    if self.ball_free==True or self.team_possessing_ball!=T_no:
                        self.move_player(T_no,self.team[T_no].formation[2]+pln,self.ball)

                else:
                    if sign*self.team[T_no].midfielders[pln][0]< sign*BC:
                        self.team[T_no].midfielders[pln][0]+=sign*self.player_run * self.team[T_no].player_speeds[pln + offset]

                        if self.team[T_no].midfielders[pln][1]>updiv:
                            self.team[T_no].midfielders[pln][1]-=self.player_run*self.team[T_no].player_speeds[pln+offset]
                        elif self.team[T_no].midfielders[pln][1]<ldiv:
                            self.team[T_no].midfielders[pln][1]+=self.player_run*self.team[T_no].player_speeds[pln+offset]
                    else :
                        self.team[T_no].midfielders[pln]=self.move_player_random(self.team[T_no].midfielders[pln], T_no, pln + offset)

                        
    
    def move_midfielders(self,T_no):
        if T_no==1:
            sign=1
            otno=2
        else:
            otno=1
            sign=-1
        
        if self.team_possessing_ball==T_no:
            
            if self.player_possessing_ball[1]>5:
                own_pl=min(8*self.length/20-self.player_gap,sign*(self.player_withball_pos[0]+sign*self.player_gap))
                own_pl*=sign
                
            elif self.player_possessing_ball[1]<self.team[T_no].formation[2]:
                own_pl=self.player_withball_pos[0]-sign*self.player_gap
            else:
                own_pl=min(8*self.length/20-self.player_gap,sign*(self.player_withball_pos[0]))
                own_pl*=sign
                
            self.move_a_midfielder(T_no,sign,own_pl)
                
        elif self.team_possessing_ball!=T_no:
                            
            if self.player_possessing_ball[1]>5:
                opponent_pl=min(8*self.length/20-self.player_gap,-sign*(self.player_withball_pos[0]-sign*self.player_gap))
                opponent_pl*=-sign
                
            elif self.player_possessing_ball[1]>=self.team[T_no].formation[2]:
                opponent_pl=min(8*self.length/20-self.player_gap,-sign*self.player_withball_pos[0])
                opponent_pl*=-sign
            else:
                opponent_pl=min(8*self.length/20-self.player_gap,-sign*self.player_withball_pos[0])
                opponent_pl*=-sign

           # print "Opponent Pl_no:",opponent_pl
                    
            self.move_a_midfielder(T_no,-sign,opponent_pl)   


    def move_a_defender(self,T_no,sign,BC):
        offset = 6
        for pln in range(4):
            updiv=-self.breadth/2 + 2*(pln+1)*self.breadth/9
            ldiv=-self.breadth/2 + (2*pln+1)*self.breadth/9
            if self.player_possessing_ball!=[T_no,pln+6]:
                if self.ball_in_player_range(self.team[T_no].defenders[pln]) and not self.Foul:
                    if self.ball_free or self.team_possessing_ball!=T_no:
                        self.move_player(T_no,pln+6,self.ball)
                else:
                    if sign*self.team[T_no].defenders[pln][0]< sign*BC:
                        self.team[T_no].defenders[pln][0]+=(sign*self.player_run) * self.team[T_no].player_speeds[pln + offset]
                        if self.team_possessing_ball==T_no:
                            if self.team[T_no].defenders[pln][1]>updiv:
                                self.team[T_no].defenders[pln][1]-=self.player_run*self.team[T_no].player_speeds[pln + offset]
                            elif self.team[T_no].defenders[pln][1]<ldiv:
                                self.team[T_no].defenders[pln][1]+=self.player_run*self.team[T_no].player_speeds[pln + offset]
                        elif not self.ball_free and pln>0 and pln<3 and self.player_possessing_ball[1]<self.team[self.team_possessing_ball].formation[2]:
                            if self.team[T_no].defenders[pln][1]>self.ball[1]:
                                self.team[T_no].defenders[pln][1]-=self.player_walk*self.team[T_no].player_speeds[pln + offset]
                            elif self.team[T_no].defenders[pln][1]<self.ball[1]:
                                self.team[T_no].defenders[pln][1]+=self.player_walk*self.team[T_no].player_speeds[pln + offset]
                        else:
                            if self.team[T_no].defenders[pln][1]>updiv:
                                self.team[T_no].defenders[pln][1]-=self.player_run*self.team[T_no].player_speeds[pln + offset]
                            elif self.team[T_no].defenders[pln][1]<ldiv:
                                self.team[T_no].defenders[pln][1]+=self.player_run*self.team[T_no].player_speeds[pln + offset]
                    else:
                        self.team[T_no].defenders[pln]=self.move_player_random(self.team[T_no].defenders[pln], T_no, pln + offset)
 #           elif self.ball_free:
 #               self.team[T_no].defenders[pln][0] -= self.player_run * self.team[T_no].player_speeds[pln + offset]
                
    
    def move_defenders(self,T_no):
        if T_no==1:
            sign=1
        else:
            sign=-1
        if self.team_possessing_ball==T_no:
            if self.player_possessing_ball[1]<self.team[T_no].formation[2]:
                own_pl=self.player_withball_pos[0]-sign*self.player_gap*2
            elif self.player_possessing_ball[1]<6:
                own_pl=self.player_withball_pos[0]-sign*self.player_gap
            else:
                own_pl=self.player_withball_pos[0]

            self.move_a_defender(T_no,sign,own_pl)
           
        elif self.team_possessing_ball!=T_no:
            if self.player_possessing_ball[1]<self.team[T_no].formation[2]:
                opponent_pl=self.player_withball_pos[0]
            elif self.player_possessing_ball[1]<6:
                opponent_pl=min(8*self.length/20,-sign*(self.player_withball_pos[0]-sign*self.player_gap))
                opponent_pl*=-sign
            else:
                opponent_pl=min(8*self.length/20,-sign*(self.player_withball_pos[0]-sign*self.player_gap*2))
                opponent_pl*=-sign

            self.move_a_defender(T_no,-sign,opponent_pl)

    def move_goalkeeper(self,T_no):
        otno =  1
        sign = 1
        if T_no==1:
            sign=-1
            otno = 2
        
        run_towards_ball = True
        #print "Entered condition!"
        for pl_pos in self.team[T_no].player_positions[:10]:
            run_towards_ball = True
            if T_no == 1 and pl_pos[0] < self.ball[0] or T_no == 2 and pl_pos[0] > self.ball[0]:
                run_towards_ball = False
                break

        if run_towards_ball and math.fabs(self.ball[0]) > self.length * 0.2:
            #print "Should run!"
            pos1 = self.team[T_no].goalkeeper
            pos2 = self.ball
            distance=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
            if int(distance)==0:
                return
            
            cosine=(pos2[0]-pos1[0])/distance
            sine=(pos2[1]-pos1[1])/distance
            step = self.player_run*0.8
            x=pos1[0]+step*cosine
            if math.fabs(x) < self.length * 0.3:
                x = self.length * 0.3
                if T_no == 1:
                    x = -self.length * 0.3
            y=pos1[1]+step*sine
            self.team[T_no].goalkeeper = [x, y]
        
        elif self.team_possessing_ball==T_no:
            self.move_goalkeeper_random(T_no)
            if sign*self.team[T_no].goalkeeper[0]>self.length/2:
                self.team[T_no].goalkeeper[0]=sign*self.length/2
            elif sign*self.team[T_no].goalkeeper[0]<self.length/2-5*self.goal_thickness:
                self.team[T_no].goalkeeper[0]=sign*(self.length/2-5*self.goal_thickness)
            if self.team[T_no].goalkeeper[1]>self.goal_width:
                self.team[T_no].goalkeeper[1]=self.goal_width
            elif self.team[T_no].goalkeeper[1]< -self.goal_width:
                self.team[T_no].goalkeeper[1]=-self.goal_width
                
        else:
            if self.ball_in_player_range(self.team[T_no].goalkeeper,True):
                self.move_player(T_no,10,self.ball)
            else:
                self.team[T_no].goalkeeper[1]=float(self.goal_width)/float(self.breadth)*float(self.ball[1])*2.0
                #print "Here!"
                

      
    def move_goalkeeper_random(self,T_no):
        step=self.player_run_fast
        rn=random()
        if rn<0.05:
            self.team[T_no].goalkeeper[0]+=step
        elif rn<0.5:
            self.team[T_no].goalkeeper[1]+=step
        elif rn<0.95:
            self.team[T_no].goalkeeper[1]-=step
        else:
            self.team[T_no].goalkeeper[0]-=step
       
    
    def move_player_random(self,position, T_no, pl_no):
        step=self.player_run * self.team[T_no].player_speeds[pl_no]
        rn=random()
        #print "Random", position
        if rn<0.3:
            position[0]+=step
        elif rn<0.5:
            position[1]+=step
        elif rn<0.8:
            position[0]-=step
        else:
            position[1]-=step
        return position


    def ball_in_player_range(self,player_pos,goalkeeper=False):
        plrange=self.player_range
        if goalkeeper:
            plrange*=2
        if self.penalty:
            plrange *= 1.5
        if (self.ball[0]< player_pos[0]+plrange and
            self.ball[0]> player_pos[0]-plrange and
            self.ball[1]< player_pos[1]+plrange and
            self.ball[1]> player_pos[1]-plrange):
            return True
        return False

    def player_in_ball_range(self,player_pos,goalkeeper):
        plrange=self.length/60
        if goalkeeper:
            plrange=plrange*1.5
        if (player_pos[0]< self.ball[0]+plrange and
            player_pos[0]> self.ball[0]-plrange and
            player_pos[1]< self.ball[1]+plrange and
            player_pos[1]> self.ball[1]-plrange):
            return True
        return False

    def check_for_possession(self):
#        if self.ball[2]<self.player_height:
        for T_no in range(1,3):
            OT_no = 1
            if T_no == 1:
                OT_no = 2
            goalkeeper=False
            for i in range(len(self.team[T_no].player_positions)):
                if i==10:
                    goalkeeper=True
                
                # #print "check for posse" ,self.team[T_no].player_positions[i]

                if self.player_in_ball_range(self.team[T_no].player_positions[i],goalkeeper):
                    if self.player_possessing_ball!=[T_no,i]:
                        player_possessing_ball = self.team[T_no].player_positions[i]
                        if i<self.team[T_no].formation[2] and self.team_possessing_ball==T_no and ((T_no == 1 and player_possessing_ball[0] > 0) or (T_no == 2 and player_possessing_ball[0] < 0)):
                            
                            ok=False
                            for item in self.team[OT_no].player_positions[:10]:
                                if T_no == 1:
                                    if player_possessing_ball[0] < item[0]:
                                        ok=True
                                else:
                                    if player_possessing_ball[0] > item[0]:
                                        ok=True

                            if not ok:
                                self.plot_players('Off side!')
                                time.sleep(2)
                                self.replay("Off side!")
                                time.sleep(0.5)
                                self.ball = self.team[OT_no].goalkeeper
                                self.team_possessing_ball=OT_no
                                self.player_possessing_ball=[OT_no,10]
                                self.player_withball_pos=self.team[OT_no].goalkeeper
                                self.ball_free=False
                                self.ball_path=[]
                                return

                        self.team_possessing_ball=T_no
                        self.player_possessing_ball=[T_no,i]
                        self.player_withball_pos=self.team[T_no].player_positions[i]
                        self.ball_free=False
                        self.ball_path=[]
                        return
    

    def move_ball(self,pos1,pos2,shot):
        self.last_kicked_pos = pos1
        #  #print "Inside moveball"
        self.ball_path=[]
        #  #print pos1
        #  #print pos2
        #  #print "Inside moveball"
        T_no = self.team_possessing_ball
        kicking_speed = self.team[T_no].kicking_speeds[self.player_possessing_ball[1]]
        distance=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
        if int(distance) == 0:
            return
      
        if shot==1:
            step_size=self.ball_speed_slow * kicking_speed
        elif shot==2:
            step_size=self.ball_speed_fast * kicking_speed
        elif shot==3:
            self.team[T_no].goal_attempts += 1
            step_size=self.ball_goal_hit
            Rn=random()*2*self.goal_width-self.goal_width * kicking_speed
            Rn = Rn * 1.5
            pos2[1]=Rn
            if math.fabs(pos2[1]) < self.goal_width:
                self.team[T_no].goal_attempts_on_target += 1
        elif shot==4:
            if distance>self.breadth/2:
                step_size=self.ball_speed_slow
            else:
                step_size=self.ball_speed_slow*0.8
                
        cosine=(pos2[0]-pos1[0])/distance
        sine=(pos2[1]-pos1[1])/distance
            

      #  #print step_size,sine,cosine
        x=pos1[0]
        y=pos1[1]
        while step_size>self.player_walk:
            x+=step_size*cosine
            y+=step_size*sine
            if shot==2:
                if x<distance/2:
                    z=x
                elif x<distance:
                    z=distance-x
                else:
                    z=0
            elif shot==3:
                if x<distance/2:
                    z=x/distance
                elif x<distance:
                    z=(distance-x)/distance
                else:
                    z=0
            z=0
            step_size-=step_size*0.08*0.2
            self.ball_path.append([x,y,z])

        self.ball_path=self.ball_path[::-1]
        self.ball_free=True
       # #print "Going out of move ball"
       # #print self.ball_path
       # #print "********"

    def move_player(self,T_no,pl_pos,pos2,slow=0):
        if pl_pos<self.team[T_no].formation[2]:
            pos1=self.team[T_no].forwards[pl_pos]
        elif pl_pos<6:
            pos1=self.team[T_no].midfielders[pl_pos-self.team[T_no].formation[2]]
        elif pl_pos<10:
            pos1=self.team[T_no].defenders[pl_pos-6]
        else:
            pos1=self.team[T_no].goalkeeper
        
        distance=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
        if int(distance)==0:
            return
            
        cosine=(pos2[0]-pos1[0])/distance
        sine=(pos2[1]-pos1[1])/distance
        if slow==0:
            step=self.player_run * self.team[T_no].player_speeds[pl_pos]
        elif slow==1:
            step=self.player_walk * self.team[T_no].player_speeds[pl_pos]
        if pl_pos == 10:
            step = step * 2
        x=pos1[0]+step*cosine
        y=pos1[1]+step*sine
        
        if pl_pos<self.team[T_no].formation[2]:
            self.team[T_no].forwards[pl_pos]=[x,y]
        elif pl_pos<6:
            self.team[T_no].midfielders[pl_pos-self.team[T_no].formation[2]]=[x,y]
        elif pl_pos<10:
            self.team[T_no].defenders[pl_pos-6]=[x,y]
        else:
            self.team[T_no].goalkeeper=[x,y]
            
    
    def opponent_player_in_range(self,OT_no,player_pos):
        self.get_player_positions()
        for item in self.team[OT_no].player_positions:
            if (item[0]< player_pos[0]+self.player_range*0.5 and
                item[0]> player_pos[0]-self.player_range*0.5 and
                item[1]< player_pos[1]+self.player_range*0.5 and
                item[1]> player_pos[1]-self.player_range*0.5):
                return True

        return False

    def opponent_player_in_range_striker(self,OT_no,player_pos):
        self.get_player_positions()
        for item in self.team[OT_no].player_positions:
            if OT_no == 2:
                if (item[0]> player_pos[0] and
                    item[0]< player_pos[0] + self.player_range and
                    item[1]< player_pos[1]+self.player_range*0.2 and
                    item[1]> player_pos[1]-self.player_range*0.2):
                    return True
            else:
                if (item[0]< player_pos[0] and
                    item[0]> player_pos[0] - self.player_range and
                    item[1]< player_pos[1]+self.player_range*0.2 and
                    item[1]> player_pos[1]-self.player_range*0.2):
                    return True
        return False

    def oppl_in_passing_range(self,OT_no,pos1,pos2):
        distance=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
        if distance == 0:
            return
        cosine=(pos2[0]-pos1[0])/distance
        sine=(pos2[1]-pos1[1])/distance
        x=pos1[0]
        y=pos1[1]
        var_dist=sqrt(pow((y-pos1[1]),2)+pow((x-pos1[0]),2))
        
        while var_dist<distance:
            x+=self.player_range*cosine
            y+=self.player_range*sine
            var_dist=sqrt(pow((y-pos1[1]),2)+pow((x-pos1[0]),2))
            if self.opponent_player_in_range(OT_no,[x,y]):
                return True

        return False

    def move_player_forward(self,T_no,position):
        if T_no==1:
            sign=1
        else:
            sign=-1
        rn=random()
        pl_no = self.player_possessing_ball[1]
        speed_factor = self.team[T_no].player_speeds[pl_no]
        if rn<0.4:
            position[0]+=sign*self.player_run* speed_factor

            if position[1]<0:
                position[1]+=self.player_run * speed_factor
            else:
                position[1]-=self.player_run * speed_factor
            
        elif rn <0.8:
            position[0]+=sign*self.player_run * speed_factor
            position[1]+=self.player_walk * speed_factor
        else:
            position[0]+=sign*self.player_run * speed_factor
            position[1]-=self.player_walk * speed_factor

        return position

    def pass_common(self, passing_pl_pos, position, pl_no, T_no):
        x = passing_pl_pos[1]-position[1]
        y = passing_pl_pos[0]-position[0]
        distance=sqrt(pow(x,2)+pow(y,2))
        if distance == 0:
            return
        # TODO
        angle = math.atan2(x, y) + (random() - 0.5) * \
                self.team[T_no].pass_angle_ratings[pl_no] * math.pi / 180.0
        ##print math.atan2(y, x), angle, x, y
        ##print passing_pl_pos
        passing_pl_pos[0] = position[0] + distance * cos(angle)
        passing_pl_pos[1] = position[1] + distance * sin(angle)
        ##print passing_pl_pos
        ##print ""
        if distance<self.length/3:
            self.move_ball(position,passing_pl_pos,self.ball_pass['grd_pass'])
        else:
            self.move_ball(position,passing_pl_pos,self.ball_pass['air_pass'])

    def pass_ball_to_striker(self):
        # #print "Pass to striker"
        T_no=self.team_possessing_ball
        player=self.player_possessing_ball
        position=self.player_withball_pos
        if T_no==1:
            sign=1
            Otno=2
        else:
            sign=-1
            Otno=1
        pl_numbers=range(0,self.team[T_no].formation[2])
        pl_not_moved=1
        while len(pl_numbers):
            pl_no=choice(pl_numbers)
            if pl_no!=player[1]:
                passing_pl_pos=self.team[T_no].forwards[pl_no]
                if not self.opponent_player_in_range(Otno,passing_pl_pos):
                    if not self.oppl_in_passing_range(Otno,position,passing_pl_pos):
                        self.pass_common(passing_pl_pos, position, pl_no, T_no)
                        return
            
            pl_numbers.remove(pl_no)
                       
    def pass_ball_to_midfielder(self):
        ##print "Pass to midfielder"
        T_no=self.team_possessing_ball
        player=self.player_possessing_ball
        position=self.player_withball_pos
        if T_no==1:
            sign=1
            Otno=2
        else:
            sign=-1
            Otno=1
        pl_numbers=range(0,self.team[T_no].formation[1])
        pl_not_moved=1
        while len(pl_numbers):
            pl_no=choice(pl_numbers)
            if pl_no!=player[1]-self.team[T_no].formation[2]:
                passing_pl_pos=self.team[T_no].midfielders[pl_no]
                if not self.opponent_player_in_range(Otno,passing_pl_pos):
                    if not self.oppl_in_passing_range(Otno,position,passing_pl_pos):
                        self.pass_common(passing_pl_pos, position, pl_no, T_no)
                        return
            
            pl_numbers.remove(pl_no)
                        
            
    def pass_ball_to_defender(self):
        ##print "pass to defender"
        T_no=self.team_possessing_ball
        player=self.player_possessing_ball
        position=self.player_withball_pos
        if T_no==1:
            sign=1
            Otno=2
        else:
            sign=-1
            Otno=1
        pl_numbers=range(0,4)
        pl_not_moved=1
        while len(pl_numbers):
            pl_no=choice(pl_numbers)
            if pl_no!=player[1]-6:
                passing_pl_pos=self.team[T_no].defenders[pl_no]
                if not self.opponent_player_in_range(Otno,passing_pl_pos):
                    if not self.oppl_in_passing_range(Otno,position,passing_pl_pos):
                        self.pass_common(passing_pl_pos, position, pl_no, T_no)
                        return
            
            pl_numbers.remove(pl_no)
                            
    
    def move_player_with_ball(self):
        striker=False
        defender=False
        midfielder=False
        T_no=self.team_possessing_ball
        player=self.player_possessing_ball
        position=self.player_withball_pos
        if player[1]<self.team[T_no].formation[2]:
            striker = True
        elif player[1]<6:
            midfielder = True
        elif player[1]<10:
            defender=True
        else:
            goalkeeper=True
        
        if T_no==1:
            sign=1
            Otno=2
        else:
            sign=-1
            Otno=1

        if striker:
            if self.opponent_player_in_range_striker(Otno,position):
                Rn=random()
                if Rn<0.3:
                    # #print "Random striker"
                    self.team[T_no].forwards[player[1]]=self.move_player_random(position, T_no, self.player_possessing_ball[1])
                    self.ball=self.team[T_no].forwards[player[1]]
                else:
                    # #print "inside else"
                    if sign*position[0]>self.length/4:
                        Rn=random()
                        if Rn<0.5:
                            self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                    if not self.ball_free:
                        self.pass_ball_to_striker()
                        
                    if not self.ball_free:
                        if sign*position[0]>self.length/6:
                            Rn=random()
                            if Rn<0.5:
                                self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                    if not self.ball_free:
                        self.pass_ball_to_midfielder()

                    if not self.ball_free:
                        self.ball=self.team[T_no].forwards[player[1]]=self.move_player_random(position, T_no , self.player_possessing_ball[1])

            else :
                if math.fabs(position[0])>self.length/4:
                    Rn=random()
                    if Rn>0.02:
                        self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                if not self.ball_free:
                    Rn=random()
                    #if Rn>0.05:
                    if True:
                        # #print "inside rn striker"
                        self.ball=self.team[T_no].forwards[player[1]]=self.move_player_forward(T_no,position) 
                    else:
                        #print "Passing Ball"
                        self.pass_ball_to_striker()
                        if not self.ball_free:
                            self.pass_ball_to_midfielder()
                        if not self.ball_free:
                            self.ball=self.team[T_no].forwards[player[1]]=self.move_player_forward(T_no,position)


        elif midfielder:
            # #print "in midfielder"
            if self.opponent_player_in_range(Otno,position):
               
                Rn=random()
                if Rn<0.2:
                    # #print "Rn1 midfielder"
                    self.ball=self.team[T_no].midfielders[player[1]-self.team[T_no].formation[2]]=self.move_player_random(position, T_no, self.player_possessing_ball[1])
                    self.ball_path=[]
                else :
                    self.pass_ball_to_striker()

                    if not self.ball_free:
                        self.pass_ball_to_midfielder()

                    if not self.ball_free:
                        if sign*position[0]>self.length/6:
                            Rn=random()
                            if Rn<0.5:
                                self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                    if not self.ball_free:
                         self.pass_ball_to_defender()
                    
                    if not self.ball_free:
                        self.ball=self.team[T_no].midfielders[player[1]-self.team[T_no].formation[2]]=self.move_player_random(position, T_no, self.player_possessing_ball[1])

            else:
                Rn=random()
                if Rn>0.05:
                    if sign*position[0]>self.length/4:
                        Rn=random()
                        if Rn<0.5:
                            self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                    else:
                        # #print "Else random"
                        self.ball=self.team[T_no].midfielders[player[1]-self.team[T_no].formation[2]]=self.move_player_forward(T_no,position)
                    
                else:
                    # #print "passing ball"
                    self.pass_ball_to_striker()
                    if not self.ball_free:
                        self.pass_ball_to_midfielder()
                    if not self.ball_free:
                        self.ball=self.team[T_no].midfielders[player[1]-self.team[T_no].formation[2]]=self.move_player_forward(T_no,position)

        elif defender:
            if self.opponent_player_in_range(Otno,position):
                Rn=random()
                if Rn<0.2:
                    self.ball=self.team[T_no].defenders[player[1]-6]=self.move_player_random(position, T_no, self.player_possessing_ball[1])
                else :
                    self.pass_ball_to_midfielder()

                    if not self.ball_free:
                        self.pass_ball_to_defender()

                    if not self.ball_free:
                        self.pass_ball_to_striker()

                    if not self.ball_free:
                        self.ball=self.team[T_no].defenders[player[1]-6]=self.move_player_random(position, T_no, self.player_possessing_ball[1])

            else :
                Rn=random()
                if Rn>0.05:
                    if sign*position[0]>self.length/4:
                        Rn=random()
                        if Rn<0.5:
                            self.move_ball(position,[sign*self.length/2,0],self.ball_pass['goal_hit'])
                    else:
                        self.ball=self.team[T_no].defenders[player[1]-6]=self.move_player_forward(T_no,position)
                else:
                    self.pass_ball_to_midfielder()
                    if not self.ball_free:
                        self.pass_ball_to_defender()
                    if not self.ball_free:
                        self.pass_ball_to_striker()
                    if not self.ball_free:
                        self.ball=self.team[T_no].defenders[player[1]-6]=self.move_player_forward(T_no,position)
            

        elif goalkeeper:

            time.sleep(0.1)
            self.move_goalkeeper_random(T_no)
            self.ball=copy.deepcopy(self.team[T_no].goalkeeper)
            self.move_players_for_goalkick(T_no)
            self.pass_ball_to_midfielder()  
            if not self.ball_free:
                self.pass_ball_to_defender()
                
            if not self.ball_free:
                self.pass_ball_to_striker()
                
            if not self.ball_free:
                self.move_goalkeeper_random(T_no)
                self.ball=copy.deepcopy(self.team[T_no].goalkeeper)
            
            time.sleep(0.05)
            


    def check_for_goal(self):
        goal_team = 0
        if self.ball[0]>self.length/2 and self.ball[1]<self.goal_width and self.ball[1]>-self.goal_width:
            if self.last_kicked_pos[0] > 0:
                goal_team = 1
                self.team[1].goals+=1
                self.ball=[0,0,0]
                self.toss=2
                self.ball_path=[]
                self.game=False
            else:
                #print self.last_kicked_pos
                self.ball = copy.deepcopy(self.team[2].goalkeeper)
                self.team_possessing_ball = 2
                self.player_possessing_ball = [2, 10]
                self.player_withball_pos = copy.deepcopy(self.team[2].goalkeeper)
                self.ball_free=False
                self.plot_players("Not a Goal !")
                time.sleep(0.15)
                #print self.ball
                #print "Exit"
                return

        elif self.ball[0]<-self.length/2 and self.ball[1]<self.goal_width and self.ball[1]>-self.goal_width:
            if self.last_kicked_pos[0] < 0:
                goal_team = 2
                self.team[2].goals+=1
                self.ball=[0,0,0]
                self.toss=1
                self.ball_path=[]
                self.game=False
            else:
                #print self.last_kicked_pos
                self.ball = copy.deepcopy(self.team[1].goalkeeper)
                self.team_possessing_ball = 1
                self.player_possessing_ball = [1, 10]
                self.player_withball_pos = copy.deepcopy(self.team[1].goalkeeper)
                self.ball_free=False
                self.plot_players("Not a Goal !")
                time.sleep(0.15)
                #print self.ball
                #print "eXit"
                return

        ##print "Inside check goal"
        ##print sum_dist
        
        if not self.game:
            time.sleep(0.1)
            self.replay("Goal for " + TEAM_NAMES[goal_team] + "!")
            self.back_to_orig_pos(goal_team)

            time.sleep(0.2)

    def back_to_orig_pos(self, goal_team = 0):
        time.sleep(1)
        all_players_back = False
        #while sum_dist[1] > 20*self.player_run_fast or sum_dist[2] > 15*self.player_run_fast:
        while not all_players_back:
            all_players_back = True
            for T_no in range(1,3):
                for plno in range(11):
                    current_pos=self.team[T_no].player_positions[plno]
                    original_pos=self.team[T_no].starting_positions[plno]
                    dist=sqrt(pow((original_pos[1]-current_pos[1]),2)+pow((original_pos[0]-current_pos[0]),2))
                    if dist>self.player_run_fast:
                        self.move_player(T_no,plno,original_pos)
                        all_players_back = False


            time.sleep(0.07)
            if goal_team > 0:
                self.plot_players('Goal for Team ' + TEAM_NAMES[goal_team] + '!')
            else:
                self.plot_players('Half time!')
                self.game=False
                

        return

    def move_players_for_goalkick(self,tno):
        if tno==1:
            step=self.player_run
            bc=-self.length/8
        else:
            step=-self.player_run
            bc=self.length/8

        players_out = False
        #print "Hee hee!"
        
        while not players_out:
            for T_no in [1,2]:
                index=0
                players_out = True
                self.get_player_positions()
                for item in self.team[T_no].player_positions[:10]:
                    if (tno==1 and item[0]<bc) or (tno==2 and item[0]>bc):
                        Rn=random()
                        if Rn<0.5:
                            new_pos = [item[0]+step,item[1]]
                        elif Rn<0.75 and Rn>0.5:
                            new_pos = [item[0]+step,item[1]+step]
                        else:
                            new_pos = [item[0]+step,item[1]-step]
                            
                        self.move_player(T_no, index, new_pos)

                        players_out = False

                    else:
                        if random()<0.5:
                            new_pos = [item[0]+step,item[1]]
                        elif random()<0.75:
                            new_pos = [item[0]+step,item[1]+step]
                        else:
                            new_pos = [item[0]+step,item[1]-step]
                            
                        self.move_player(T_no, index, new_pos)


                    index+=1
                self.plot_players()
                time.sleep(0.04)
                self.check_players_out()                        
                    
    

    def check_ball_moving_towards_u(self,item):
        for pos in self.ball_path:
            if (pos[0]<item[0]+self.player_range*1.2 and
                pos[0]>item[0]-self.player_range*1.2 and
                pos[1]<item[1]+self.player_range*1.2 and
                pos[1]>item[1]-self.player_range*1.2) :

                return True

        return False
        
    
    def move_for_possession(self):
                
        for Tnpb in range(1,3):
            index=0
            for item in self.team[Tnpb].player_positions:
                if [Tnpb,index]!=self.player_possessing_ball:
                    if self.check_ball_moving_towards_u(item):
                        self.move_player(Tnpb,index,self.ball,1)

    def nearest_player(self, point):
        throwing_team = 1
        if self.team_possessing_ball == 1:
            throwing_team = 2
        distances = []
        for i in self.team[throwing_team].player_positions[:10]:
            distances.append(sqrt((i[0] - point[0])**2 + (i[1] - point[1])**2))
        return (throwing_team, distances.index(min(distances)))


    def nearest_pass_player(self,pos):
        distances = []
        tno=self.team_possessing_ball
        if tno==1:
            optno=2
        else:
            optno=1
        #self.get_player_positions()
        for item in self.team[tno].player_positions[:10]:
            if item!=self.player_withball_pos:
                distances.append(sqrt((item[0] - pos[0])**2 + (item[1] - pos[1])**2))
            else:
                distances.append(self.length)

        sorteddist=[]
        #print "distances",distances
        sorteddist=copy.deepcopy(distances)
        sorteddist.sort()
        #print sorteddist
        for item in sorteddist:
            index=distances.index(item)
            #return index
            if not self.opponent_player_in_range(optno,self.team[tno].player_positions[index]):
                if not self.oppl_in_passing_range(optno,self.ball,self.team[tno].player_positions[index]):
                    return index
                    
        return distances.index(sorteddist[0])

    def do_out_or_corner(self,corner=False):
        throwing_team, index_thrower = self.nearest_player(self.ball)
        pos1=self.team[throwing_team].player_positions[index_thrower]
        pos2=self.ball
        dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
        self.team_possessing_ball = throwing_team
        self.player_withball_pos = self.team[throwing_team].player_positions[index_thrower]
        self.player_possessing_ball=[throwing_team,index_thrower]
        self.ball_free=False
        
        while dist>self.player_run_fast:
            self.move_player(throwing_team,index_thrower,self.ball)
            self.move_forward_players(2)
            self.move_forward_players(1)
            self.move_defenders(1)
            self.move_defenders(2)
            self.move_midfielders(1)
            self.move_midfielders(2)
            #self.move_goalkeeper(1)
            #self.move_goalkeeper(2)
            time.sleep(0.07)
            self.plot_players('Out!')
            pos1=self.team[throwing_team].player_positions[index_thrower]
            dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
            self.player_withball_pos = self.team[throwing_team].player_positions[index_thrower]
        if not corner:
            index=self.nearest_pass_player(self.ball)
            pos1=copy.deepcopy(self.ball)
            pos2=self.team[throwing_team].player_positions[index][:]
            self.move_ball(pos1,pos2,4)
            #raw_input()
        else:
            self.team[throwing_team].corners+=1
            self.pass_ball_to_striker()
            if not self.ball_free:
                self.pass_ball_to_midfielder()
            if not self.ball_free:
                self.pass_ball_to_defender()
            if not self.ball_free:
                #index=self.nearest_pass_player(self.player_withball_pos)
                pos1=copy.deepcopy(self.ball)
                pos2=self.team[throwing_team].forwards[0]
                self.move_ball(pos1,pos2,2)

    def check_ball_out(self):
        if (self.ball[1] < - self.breadth / 2 or
            self.ball[1] > + self.breadth / 2):

            self.ball[1] = signum(self.ball[1]) * (self.breadth / 2)
            self.ball_path=[]
            self.do_out_or_corner()
            
        elif (self.ball[0] < - self.length / 2 or 
              self.ball[0] > self.length / 2):

            if (self.team_possessing_ball == 2 and self.ball[0] < -self.length / 2) \
            or (self.team_possessing_ball == 1 and self.ball[0] > +self.length / 2):
                self.ball_path=[]
                if self.ball[0] < - self.length / 2:
                    tno=1
                else:
                    tno=2

                time.sleep(0.07)
                self.ball=self.team[tno].goalkeeper[:]
                self.team_possessing_ball = tno
                self.player_possessing_ball = [tno, 10]
                self.player_withball_pos = self.team[tno].goalkeeper[:]
                ## TODO
                self.move_players_outside_D()
                self.ball_free = False
                self.plot_players('Not a goal!')
                time.sleep(0.07)
            else:
                self.ball=[signum(self.ball[0])*(self.length/2-5),signum(self.ball[1])*(self.breadth/2-5)]
                self.do_out_or_corner(True)
                    
    def move_players_outside_D(self):
        opp_player_out = False
        steps = self.player_run
        while not opp_player_out:
            sign = 3 - 2 * self.team_possessing_ball
            OT_no = sign + self.team_possessing_ball
            opp_player_out = True
            for item in self.team[OT_no].player_positions[:10]:
                if math.fabs(item[0]) > self.length / 4 \
                and ((OT_no == 1 and item[0] > 0) or (OT_no == 2 and item[0] < 0)):
                    cur_player = self.team[OT_no].player_positions.index(item)
                    to_pos = [item[0] + sign * self.player_run, item[1]]
                    self.move_player(OT_no, cur_player, to_pos)
                    opp_player_out = False

            time.sleep(0.05)
            self.plot_players('Not a goal!')
                

    def build_wall(self,otno):
        tno=1
        if otno==1:
            tno=2
        pos1=self.ball
        pos2=self.team[otno].goalkeeper
        distance=sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)
        cosine=(pos2[0]-pos1[0])/distance
        sine=(pos2[1]-pos1[1])/distance
        gap=self.player_run
        midpos=[]
        midpos.append([pos1[0]+20*gap*cosine,pos1[1]+10*gap*sine])
        midpos.append([pos1[0]+20*gap*cosine+gap*sine, pos1[1]+20*gap*sine-4*gap*cosine])

        if self.team[otno].formation[2]==3:
            midpos.append([pos1[0]+20*gap*cosine-gap*sine, pos1[1]+20*gap*sine+4*gap*cosine])

        sum = 0
        for pln in range(self.team[otno].formation[2]):
            plpos=self.team[otno].forwards[pln]
            sum += sqrt((plpos[0]-midpos[pln][0])**2 + (plpos[1] - midpos[pln][1])**2)

        while sum > 3 * self.player_run:
            sum = 0
            for pln in range(self.team[otno].formation[2]):
                plpos=self.team[otno].forwards[pln]
                self.move_player(otno,pln, midpos[pln])
                plpos=self.team[otno].forwards[pln]
                sum += sqrt((plpos[0]-midpos[pln][0])**2 + (plpos[1] - midpos[pln][1])**2)
            time.sleep(0.05)
            
            self.plot_players("Free kick for Team %s" % TEAM_NAMES[tno])
            self.move_midfielders(2)
            self.move_midfielders(1)
            self.move_defenders(1)
            self.move_defenders(2)
            if otno == 1:
                self.move_forward_players(2)
            else:
                self.move_forward_players(1)
            self.move_goalkeeper(1)
            self.move_goalkeeper(2)

        self.move_players_out_freekick(otno)

        delay=0
        while delay<1:
            self.move_midfielders(2)
            self.move_midfielders(1)
            self.move_defenders(1)
            self.move_defenders(2)
            self.move_goalkeeper(1)
            self.move_goalkeeper(2)
            if otno == 1:
                self.move_forward_players(2)
            else:
                self.move_forward_players(1)

           #  for pln in range(self.team[otno].formation[1]):
#                 position=self.team[otno].midfielders[pln]
#                 self.team[otno].midfielders[pln]=self.move_player_random(position,otno,pln+self.team[otno].formation[2])
            
            self.move_players_out_freekick(otno)
            delay=delay+0.05
            time.sleep(0.07)
            self.plot_players("Free Kick for Team %d"% tno)

#        #raw_input()
        
    def move_players_out_freekick(self,otno):
        boxsize=self.player_run*15
        index=0
        players_out=False
        while not players_out:
            players_out=True
            index=self.team[otno].formation[2]
            #print players_out
            for item in self.team[otno].midfielders + self.team[otno].defenders:
                if otno==1:
                    if (item[0]<self.ball[0] and item[0]>self.ball[0]-boxsize and
                        item[1]<self.ball[1]+boxsize and
                        item[1]>self.ball[1]-boxsize):
                        if item[1]<self.ball[1]:
                            pos2=[item[0],item[1]-boxsize-10]
                        else:
                            pos2=[item[0],item[1]+boxsize+10]
                        self.move_player(otno,index,pos2)
                        players_out=False
                       
                else:
                    if (item[0]>self.ball[0] and item[0]<self.ball[0]+boxsize and
                        item[1]<self.ball[1]+boxsize and
                        item[1]>self.ball[1]-boxsize):
                        if item[1]<self.ball[1]:
                            pos2=[item[0],item[1]-boxsize-10]
                        else:
                            pos2=[item[0],item[1]+boxsize+10]
                        self.move_player(otno,index,pos2)
                        players_out=False
                        
             
                index+=1
            self.plot_players()
            #print players_out
            #print
            time.sleep(0.14)
                            
                    
    
    def check_for_foul(self):
        if self.team_possessing_ball==1:
            opteam=2
            tno=1
        else:
            opteam=1
            tno=2

        index=0
        
        for item in self.team[opteam].player_positions:
            position=self.player_withball_pos
            distance=sqrt((position[0]-item[0])**2+(position[1]-item[1])**2)
            if distance<1.5*self.player_run_fast:
                self.Foul=True
                self.team[3 - opteam].fouls += 1
                ##print "inside check foul"
                time.sleep(0.07)
                Rn=random()
                if Rn<0.25:
                    stepx=self.player_range*1.2
                    stepy=self.player_range*1.2*(2*random()-1)
                elif Rn<0.5:
                    stepx=-self.player_range*1.2
                    stepy=self.player_range*1.2*(2*random()-1)
                elif Rn<0.75:
                    stepy=self.player_range*1.2
                    stepx=self.player_range*1.2*(2*random()-1)
                else:
                    stepy=self.player_range*1.2
                    stepx=self.player_range*1.2*(2*random()-1)

                
                Rn=random()
                
                if Rn<0.5:
                    pos1=self.player_withball_pos
                    pos2=[pos1[0]+stepx,pos1[1]+stepy]
                    dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))

                    while dist>self.player_run:
                        self.move_player(tno,self.player_possessing_ball[1],pos2)
                        time.sleep(0.07)
                        self.plot_players('Foul!')
                        pos1=self.team[tno].player_positions[self.player_possessing_ball[1]]
                        dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))

                    self.player_withball_pos=item
                    self.team_possessing_ball=opteam
                    self.player_possessing_ball=[opteam,index]

                    
                    
                   

                else:
                    pos1=item
                    pos2=[pos1[0]+stepx,pos1[1]+stepy]
                    dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
                    while dist>self.player_run:
                        self.move_player(opteam,index,pos2)
                        time.sleep(0.07)
                        self.plot_players('Foul!')
                        pos1=self.team[opteam].player_positions[index]
                        dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))

                        

                if self.ball[0] < - self.length*0.3 and math.fabs(self.ball[1]) < self.breadth * 0.25 and self.team_possessing_ball == 2:
                    self.ball=[-0.325*self.length,0]
                    self.team[1].goalkeeper = [-0.48 * self.length, 0]
                    self.do_penalty(2)

                elif self.ball[0] > self.length*0.3 and math.fabs(self.ball[1]) < self.breadth * 0.25 and self.team_possessing_ball == 1:
                    self.ball=[0.325*self.length,0]
                    self.team[2].goalkeeper = [0.48 * self.length, 0]
                    self.do_penalty(1)


                    #opteam = 3 - self.team_possessing_ball
                
                elif (self.ball[0]>self.length*0.1 and self.team_possessing_ball==1) or (self.ball[0] < -self.length*0.1 and self.team_possessing_ball==2):
                    #print "Goal Kick"
                    tno=self.team_possessing_ball
                    
                                       
                    if self.player_possessing_ball[1]<self.team[tno].formation[2] or \
                           self.player_possessing_ball[1]>5:
                        
                        pos1=self.player_withball_pos
                        pos2=[pos1[0]+stepx,pos1[1]+stepy]
                        dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
                        
                        while dist>self.player_run:
                            self.move_player(tno,self.player_possessing_ball[1],pos2)
                            time.sleep(0.07)
                            self.plot_players('Foul!')
                            pos1=self.team[tno].player_positions[self.player_possessing_ball[1]]
                            dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))


                        pos1=self.team[tno].midfielders[1]
                        pos2=self.ball
                        dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
    
                        while dist>self.player_run:
                            self.move_player(tno,self.team[tno].formation[2]+1,pos2)
                            time.sleep(0.07)
                            self.move_midfielders(2)
                            self.move_midfielders(1)
                            self.move_defenders(1)
                            self.move_defenders(2)
                            self.move_forward_players(2)
                            self.move_forward_players(1)
                            self.move_goalkeeper(1)
                            self.move_goalkeeper(2)

                            self.plot_players('Foul!')
                            pos1=self.team[tno].midfielders[1]
                            dist=sqrt(pow((pos2[1]-pos1[1]),2)+pow((pos2[0]-pos1[0]),2))
    
                        self.player_withball_pos=self.team[tno].midfielders[1]
                        self.player_possessing_ball=[tno,self.team[tno].formation[2]+1]
                    
                    opteam = 3 - self.team_possessing_ball

                    self.build_wall(opteam)
                    position=self.ball[:]
                    if random()<0.7:
                        sign = opteam - self.team_possessing_ball
                        self.move_ball(position,[sign*self.length/2,0], self.ball_pass['goal_hit'])
                    else:
                        self.pass_ball_to_striker()
                        if not self.ball_free:
                            self.pass_ball_to_midfielder()  
                        if not self.ball_free:
                            #print "was here happy"
                            pos1=self.ball
                            pos2=self.team[tno].forwards[0]
                            self.move_ball(pos1,pos2,1)
                     
                else:
                    delay=0
                    while delay<1:
                        self.move_forward_players(2)
                        self.move_forward_players(1)
                        self.move_defenders(1)
                        self.move_defenders(2)
                        self.move_midfielders(1)
                        self.move_midfielders(2)
                        self.move_goalkeeper(1)
                        self.move_goalkeeper(2)
                        time.sleep(0.07)
                        delay=delay+0.09
                        self.plot_players()
                    
                    tno=self.team_possessing_ball
                    if self.player_possessing_ball[1]<6:
                        self.pass_ball_to_striker()
                        if not self.ball_free:
                            self.pass_ball_to_midfielder()
                        if not self.ball_free:
                            self.pass_ball_to_defender()
                        if not self.ball_free:
                            if self.player_possessing_ball[1] != self.team[tno].formation[2]:
                                self.move_ball(self.ball, self.team[tno].midfielders[0], 0)
                            else:
                                self.move_ball(self.ball, self.team[tno].midfielders[1], 0)
                    else:
                        self.pass_ball_to_midfielder()
                        if not self.ball_free:
                            self.pass_ball_to_defender()
                        if not self.ball_free:
                            self.pass_ball_to_striker()
                        if not self.ball_free:
                            self.move_ball(self.ball, self.team[tno].midfielders[0], 0)
                            
                         
                return
            index+=1
        self.Foul=False

    def do_penalty(self,tno):
        #print "in do penalty"
        player_out = False
        steps = self.player_run
        if tno==2:
            sign=1
        else:
            sign=-1
          
        while not player_out:
            player_out = True
            for T_no in [1,2]:
                for item in self.team[T_no].player_positions[:10]:
                    if (tno==1 and item[0] > self.length / 4) or (tno==2 and item[0] < -self.length / 4) :
                        cur_player = self.team[T_no].player_positions.index(item)
                        to_pos = [item[0] + sign * self.player_run, item[1]]
                        self.move_player(T_no, cur_player, to_pos)
                        player_out = False
                time.sleep(0.02)
                self.plot_players('Penalty! for Team %d' % tno)

        pos1=self.team[tno].forwards[0]
        pos2=[-sign*self.length/4,0]

        distance=sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)

        while distance>self.player_run:
            self.move_player(tno,0,pos2)
            pos1=self.team[tno].forwards[0]
            distance=sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)
            time.sleep(0.02)
            self.plot_players()
            
        time.sleep(0.3)
        #print "First stage over"
        
        pos2=self.ball
        pos1=self.team[tno].forwards[0]
        distance=sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)

        while distance>self.player_run:
            self.move_player(tno,0,pos2)
            pos1=self.team[tno].forwards[0]
            distance=sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)
            time.sleep(0.02)
            self.plot_players()

        time.sleep(1)
        #print "Exit"
        self.penalty=True
        self.move_ball(pos2,[-sign*self.length/2,0],self.ball_pass['goal_hit'])
        self.penalty=False
        
      
        
    def check_players_out(self):
        for tno in range(1,3):
            index=0
            for item in self.team[tno].player_positions:
                if item[1]>9*self.breadth/20:
                    pos2=[item[0]+self.player_run,item[1]-self.player_run*10]
                    self.move_player(tno,index,pos2)
                elif item[1]<-9*self.breadth/20:
                    pos2=[item[0]+self.player_run,item[1]+self.player_run*10]
                    self.move_player(tno,index,pos2)
                if item[0]>9*self.length/20:
                    pos2=[item[0]-20*self.player_run,item[1]]
                    self.move_player(tno,index,pos2)
                elif item[0]<-9*self.length/20:
                    pos2=[item[0]+20*self.player_run,item[1]]
                    self.move_player(tno,index,pos2)
                
                index+=1

        
    def move_all_towards_ball(self):
        players_right_side=True
        players_left_side=True
        for T_no in [1,2]:
            for item in self.team[T_no].player_positions[:10]:
                if item[0]>self.ball[0]:
                    players_left_side=False
                else:
                    players_right_side=False

        step_size=0
        if players_right_side:
            step_size=-self.player_run
        elif players_left_side:
            step_size=self.player_run
            
        
        if players_right_side or players_left_side and self.ball_free:
            #print "inside move players :)"
            for T_no in [1, 2]:
                index = 0
                for item in self.team[T_no].player_positions[:10]:
                    pos2=[item[0]+step_size,item[1]]
                    if random()<0.2:
                        pos2[1]+=self.player_run
                    if random()<0.2:
                        pos2[1]-=self.player_run

                    if (item[1]< self.ball[1]+self.player_range*2 and
                        item[1]> self.ball[1]-self.player_range*2):
                        self.move_player(T_no,index,self.ball)
                    else:
                        self.move_player(T_no,index,pos2)
                    index+=1

            self.plot_players()
            time.sleep(0.02)
            self.check_for_possession()
        
                    
        
    def play_simulation(self,time_step):
        self.time=0
        self.draw_ground()
        self.scale_down(time_step)
        self.scale_up(2)
        #count=0
        while True:
            if self.game==False:
                time.sleep(0.07)
                self.start_game()
      
            if self.ball_free == True:
                ##print "inside Playsimulation false"
                if len(self.ball_path)!=0:
                    self.ball=self.ball_path[-1]
                    self.ball_path.pop()
                    
                self.check_for_possession()
                self.move_for_possession()
                self.move_all_towards_ball()
            
            elif self.ball_free==False:
                ##print "inside Playsimulation false"
                self.check_for_foul()
                self.move_player_with_ball()
                
            self.move_forward_players(2)
            self.move_forward_players(1)
            self.move_defenders(1)
            self.move_defenders(2)
            self.move_midfielders(1)
            self.move_midfielders(2)
            self.move_goalkeeper(1)
            self.move_goalkeeper(2)
         #   #print "Z" ,self.ball[2]
         #   #print self.player_possessing_ball
            self.plot_players()
            time.sleep(0.07)
            ##print count
            #if count==100:
               # self.ball=[self.length/2+100,0,0]
            self.check_for_goal()
            self.check_ball_out()
            self.check_players_out()
            self.time += time_step
            self.team[self.team_possessing_ball].possession_time += time_step
            #print self.last_kicked_pos
            
            if self.time > GAME_TIME / 2 and not self.half_time_details or self.time > GAME_TIME:
                if not self.half_time_details:
                    print "STATISICS AT HALF TIME:"
                print "%-13s %-7s %-7s" % (" ", "Pinks", "Blues")
                print "%-13s %-7d %-7d" % ("Goals:", self.team[1].goals, self.team[2].goals)
                print "%-13s %-7d %-7d" % ("Attempts:", self.team[1].goal_attempts, self.team[2].goal_attempts)
                print "%-13s %-7d %-7d" % ("On target", self.team[1].goal_attempts_on_target,
                                           self.team[2].goal_attempts_on_target)
                print "%-13s %-3.2f%% %-3.2f%%" % ("Possession:",
                                                   self.team[1].possession_time / self.time * 100,
                                                   self.team[2].possession_time / self.time * 100)
                print "%-13s %-7d %-7d" % ("Fouls:", self.team[1].fouls, self.team[2].fouls)
                print "%-13s %-7d %-7d" % ("Corners:", self.team[1].corners, self.team[2].corners)
                if self.time > GAME_TIME:
                    break
                else:
                    self.half_time_details = True
                raw_input()

            if self.time >  GAME_TIME / 2 and not self.side_changed :
                #self.g.plot(self.d1,self.d2,self.d3,self.d4,self.d5,self.d6,self.d7,self.d8)
                #self.game=False
                self.pos_sign = -1
                self.ball = [0, 0]
                self.back_to_orig_pos(0)
                self.side_changed=True
            #time.sleep(0.05)
        

    def draw_ground(self):
        time.sleep(0.07)
        self.g=Gnuplot.Gnuplot()
        self.g('unset xtics')
        self.g('unset ytics')
        self.g('set yrange [%d:%d]'%(-self.breadth/2.0,self.breadth/2.0))
        self.g('set xrange [%d:%d]'%(-self.length/2.0,self.length/2.0))
        self.g('set grid on')
        self.g('set pointsize 2')
       
        t1=range(0,1000)
        t=[i/1000.0*2*3.1415 for i in t1]
#       t=arange(0,2*pi,0.01)
        x1=[sin(i)*self.length/10 for i in t]
        y1=[cos(i)*self.length/10 for i in t]
        self.d1=Gnuplot.Data(x1,y1)
        self.d1.set_option(with="lines 1")

        x2=[0.0,0.0]
        y2=[-self.breadth/2.0,self.breadth/2.0]
        self.d2=Gnuplot.Data(x2,y2)
        self.d2.set_option(with="lines 1")

        x3=[-self.length/2.0,-self.length*3.0/10.0,-self.length*3.0/10.0,-self.length/2.0]
        y3=[-self.breadth/4.0,-self.breadth/4.0,self.breadth/4.0,self.breadth/4.0]
        self.d3=Gnuplot.Data(x3,y3)
        self.d3.set_option(with="lines 1")

        x4=[self.length/2.0,self.length*3.0/10.0,self.length*3.0/10.0,self.length/2.0]
        y4=[-self.breadth/4.0,-self.breadth/4.0,self.breadth/4.0,self.breadth/4.0]
        self.d4=Gnuplot.Data(x4,y4)
        self.d4.set_option(with="lines 1")

        x5=[-self.length/2.0,-self.length*2.0/5.0,-self.length*2.0/5.0,-self.length/2.0]
        y5=[-self.breadth/8.0,-self.breadth/8.0,self.breadth/8.0,self.breadth/8.0]
        self.d5=Gnuplot.Data(x5,y5)
        self.d5.set_option(with="lines 1")

        x6=[self.length/2.0,self.length*2.0/5.0,self.length*2.0/5.0,self.length/2.0]
        y6=[-self.breadth/8.0,-self.breadth/8.0,self.breadth/8.0,self.breadth/8.0]
        self.d6=Gnuplot.Data(x6,y6)
        self.d6.set_option(with="lines 1")

        x7=[self.length/2.0,self.length/2.0-self.goal_thickness,self.length/2.0-self.goal_thickness,self.length/2.0]
        y7=[-self.goal_width,-self.goal_width,self.goal_width,self.goal_width]
        self.d7=Gnuplot.Data(x7,y7)
        self.d7.set_option(with="lines 1")

        x8=[-self.length/2.0,-(self.length/2.0-self.goal_thickness),-(self.length/2.0-self.goal_thickness),-self.length/2.0]
        y8=[-self.goal_width,-self.goal_width,self.goal_width,self.goal_width]
        self.d8=Gnuplot.Data(x8,y8)
        self.d8.set_option(with="lines 1")

    def scale_down(self,time):
        self.player_walk*=time
        self.player_run*=time
        self.player_run_fast*=time
        self.ball_goal_hit*=time
        self.ball_speed_fast*=time
        self.ball_speed_slow*=time


    def scale_up(self,factor):
        self.player_walk*=factor
        self.player_run*=factor
        self.player_run_fast*=factor
        self.ball_goal_hit*=factor
        self.ball_speed_fast*=factor
        self.ball_speed_slow*=factor

    def pop_and_append(self, my_list, element):
        if len(my_list) > HISTORY_LENGTH:
            my_list.pop(0)
        my_list.append(element)

    def history_update(self):
        #self.pop_and_append(self.ball_history, self.ball)
        #self.pop_and_append(self.team[1].history, self.team[1].player_positions)
        #self.pop_and_append(self.team[2].history, self.team[2].player_positions)
        if len(self.ball_history) > HISTORY_LENGTH:
            self.ball_history.pop(0)
        self.ball_history.append(copy.deepcopy(self.ball[:2]))
        #print "Appended: ", self.ball_history[-1]

        if len(self.team[1].history) > HISTORY_LENGTH:
            self.team[1].history.pop(0)
        self.team[1].history.append(copy.deepcopy(self.team[1].player_positions))
        if len(self.team[2].history) > HISTORY_LENGTH:
            self.team[2].history.pop(0)
        self.team[2].history.append(copy.deepcopy(self.team[2].player_positions))


    def replay(self, special=""):
        #self.draw_ground()
        x = 'r'
        while x == 'r':
            for i in range(0, HISTORY_LENGTH):
                ball=Gnuplot.Data(self.pos_sign * self.ball_history[i][0],self.ball_history[i][1])
                ball.set_option(with="points lt 1 pt 7 ps 2")
        
                #self.get_player_positions()
                
                x7=[]
                y7=[]
                for item in self.team[1].history[i]:
                    x7.append(self.pos_sign * item[0])
                    y7.append(item[1])
                    
                players1=Gnuplot.Data(x7,y7)
                players1.set_option(with="points lt 4 pt 6 ps 2.5")
        
                x8=[]
                y8=[]
                for item in self.team[2].history[i]:
                    x8.append(self.pos_sign * item[0])
                    y8.append(item[1])
    #            print x7, y7
    #            print x8, y8
                players2=Gnuplot.Data(x8,y8)
                players2.set_option(with="points lt 3 pt 6 ps 2.5")
                if self.pos_sign == 1:
                    self.g('set title "Pinks : %d  <<====>> Blues : %d" ' %(self.team[1].goals,self.team[2].goals))
                else:
                    self.g('set title "Blues : %d  <<====>> Pinks : %d" ' %(self.team[2].goals,self.team[1].goals))
                self.g('set xlabel "%s"' % ("REPLAY: " + special))
                    
                self.g.plot(self.d1,self.d2,self.d3,self.d4,self.d5,self.d6,self.d7,self.d8,players1,players2,ball)
                time.sleep(0.18)
            x = 'q'
            #raw_input()
        
    def plot_players(self, special_label = None):
        ball=Gnuplot.Data(self.pos_sign * self.ball[0],self.ball[1])
#        ball.set_option(with="points 18 6 ls 1;")
        ball.set_option(with="points lt 1 pt 7 ps 2")
        ##print "Ball: ",self.ball

        self.get_player_positions()
        
        x7=[]
        y7=[]
        for item in self.team[1].player_positions:
            x7.append(self.pos_sign * item[0])
            y7.append(item[1])
            
        players1=Gnuplot.Data(x7,y7)
        players1.set_option(with="points lt 4 pt 6 ps 2.5")
        x8=[]
        y8=[]
        for item in self.team[2].player_positions:
            x8.append(self.pos_sign * item[0])
            y8.append(item[1])
            
        players2=Gnuplot.Data(x8,y8)
        players2.set_option(with="points lt 3 pt 6 ps 2.5")
        if self.pos_sign == 1:
            self.g('set title "Pinks : %d  <<====>>  Blues : %d" ' %(self.team[1].goals,self.team[2].goals))
        else:
            self.g('set title "Blues : %d  <<====>>  Pinks : %d" ' %(self.team[2].goals,self.team[1].goals))
        if special_label:
            self.g('set xlabel "%s"' % special_label)
        else:
            now = self.time
            minutes = int(now / 60)
            seconds = str(int(now - 60 * minutes))
            if len(seconds) < 2:
                seconds = "0" + seconds
            self.g('set xlabel "%s"' % "%2d:%2s" % (minutes, seconds))
            
        self.g.plot(self.d1,self.d2,self.d3,self.d4,self.d5,self.d6,self.d7,self.d8,players1,players2,ball)
        self.history_update()
 
  
if __name__=="__main__":
    f=Football(4000,3000)
    f.make_team(1,(4,4,2), PASS_ANGLES[0], PLAYER_SPEEDS[0], KICKING_SPEEDS[0])
    f.make_team(2,(4,3,3), PASS_ANGLES[1], PLAYER_SPEEDS[1], KICKING_SPEEDS[1])
    f.play_simulation(0.2)
