"""
This code was developed by Steve Sekula in 2008 and 2009. 

Used and slightly modified by Craig Group in 2012/2013.
   --> added functionality to sort uncovered list by score 2014

Used and slightly modified by Jesus Orduna in 2015
   --> Connection files will now be read with a for loop instead of
       adding each one individually line-by-line
   --> Resulting log now contains uncontested primaries in a format
       ready to be imported to the PrimaryAssignments page on the
       wiki. In particular:
       - Rep. names and district are now links to their respective
         congressmerge.com page, this is easy as the address refers
         to state/district, for example: IL11, TX01, ... which is
         already available.
       - Senator names and state are now links to the congressmerge.com
         page for the state from there people can click on the respective
         link for the individual senator. The ending of the address is
         state/[SR|JR], for example: ILSR, ILJR, ... and there is no
         way to determine who is the senior/junior from the available
         information.
Modified by Jesus Orduna in 2016
   --> congressmerge.com was shutdown on 01/28/2016. Modifying to print
       .gov sites instead.


"""

"""Assign Primaries"""
from Classes import *
import copy
from operator import itemgetter
import glob

# load the congressperson DB
LoadCongresspersonDB("congresspersons.txt")

# score the Congresspersons based on their association with committees,
# etc.
ScoreCongressPersons()

# create the list of TeamMates
TeamMemberList = []

for aFile in glob.glob("2016_CONNECTIONS/*.txt"):
    TeamMemberList.append( createTeamMemberFromFile( aFile ) )

##--------------------------------------------------------------------------------------

# store the primary for each Congressperson
Primaries = {}

# Create a map that stores the name of a Congressperson and
# the multiple, equally-qualified individuals who contest for
# that Congressperson. 
ContestedPrimaries = {}

Congress_Person_Counter=0
for aCongressPerson in CongressPersonDB:
    Congress_Person_Counter+=1
    print aCongressPerson.name + " " + str(aCongressPerson.score)
    bestMatch = TeamMember()
    bestScore = 0
    
    for aTeamMember in TeamMemberList:
        if aTeamMember.hasConnection(aCongressPerson):
            if aTeamMember.scoreForConnection(aCongressPerson) > bestScore:
                bestScore = aTeamMember.scoreForConnection(aCongressPerson)
                bestMatch = aTeamMember
                # reset the contested primaries map for this congressperson
                if aCongressPerson.name in ContestedPrimaries:
                    del ContestedPrimaries[aCongressPerson.name]
                print "%s has connection to %s with score %d" % (aTeamMember.name,aCongressPerson.name,aTeamMember.scoreForConnection(aCongressPerson))
            elif aTeamMember.scoreForConnection(aCongressPerson) == bestScore:
                # this is a contested primary. Add this name to the list of
                # contested primaries
                if aCongressPerson.name not in ContestedPrimaries:
                    ContestedPrimaries[aCongressPerson.name] = [bestMatch]
                ContestedPrimaries[aCongressPerson.name].append(aTeamMember)
                print "%s has the same strength connection to %s (with score %d) as the current best, %s" % (aTeamMember.name,aCongressPerson.name,aTeamMember.scoreForConnection(aCongressPerson),bestMatch.name)
    if bestScore > 0:
        if aCongressPerson.name not in ContestedPrimaries:
            if Primaries.get(bestMatch.name):
                (Primaries[bestMatch.name]).append(aCongressPerson)
            else :
                Primaries[bestMatch.name] = [aCongressPerson]
        else:
            print "This member, %s, is contested and will not be added to any one primary list." % (aCongressPerson.name)

print """
#######################################################################
UNCONTESTED PRIMARIES 
#######################################################################
"""


#Store the primary list

PrimarySummaryList=[]

for aPrimary in Primaries:
    """ 
    rank the Congresspersons in the primary's list
    by their score
    """
    Primaries[aPrimary].sort()
    Primaries[aPrimary].reverse() #rank from highest to lowest in score
    
    print "== %s ==" % (aPrimary) # JO: string ready to be imported to wiki

    Count=0
    for aCongressPerson in Primaries[aPrimary]:
        # find the primary object in the primary list, based on this name
        aPrimaryObj = TeamMember()
        for aTeamMember in TeamMemberList:
            if aTeamMember.name == aPrimary:
                aPrimaryObj = aTeamMember
        Count=Count+1
        # JO: resulting string ready to be imported to wiki, with different links
        #     to .gov sites
        if aCongressPerson.state == aCongressPerson.district :
            # Senate case:
            print "[http://www.senate.gov/general/contact_information/senators_cfm.cfm?State=%s %s (%s-%s)] [SCORE=%s] [YOUR CONNECTION STRENGTH=%s]<br>" % (aCongressPerson.state,aCongressPerson.name,aCongressPerson.state,aCongressPerson.district,aCongressPerson.score,aPrimaryObj.scoreForConnection(aCongressPerson))
        else :
            # House case:
            print "[http://www.house.gov/representatives/#state_%s %s (%s-%s)] [SCORE=%s] [YOUR CONNECTION STRENGTH=%s]<br>" % (aCongressPerson.state.lower(),aCongressPerson.name,aCongressPerson.state,aCongressPerson.district,aCongressPerson.score,aPrimaryObj.scoreForConnection(aCongressPerson))
    PrimarySummaryList.append([aPrimary,Count])




    
    
          
print """
#######################################################################
CONTESTED PRIMARIES 
#######################################################################
"""

Contested_Primary_Counter=len(ContestedPrimaries)

print "There are %d contested Primaries.\n" %len(ContestedPrimaries)
for aContestedPrimary in ContestedPrimaries:
    print "%s is contested among the following people: " % (aContestedPrimary)
    for aTeamMember in ContestedPrimaries[aContestedPrimary]:
        print "     %s" % (aTeamMember.name)





print """
#######################################################################
UNCOVERED PRIMARIES 
#######################################################################
"""

#Loop over congress person list



UncoveredList=[]


for aCongressPerson in CongressPersonDB:
    isCovered=0

    #Check to see the congressperson has been added as a primary to anyone
    for aPrimary in Primaries:
        for bCongressPerson in Primaries[aPrimary]:
            if aCongressPerson.name==bCongressPerson.name:
                isCovered=1

#    for aContestedPrimary in ContestedPrimaries:
#        if aCongressPerson.name==aContestedPrimary:        
#            isCovered=1
                    

    #Append to the list of primaries that are not covered.
    if isCovered==0:
        UncoveredList.append([aCongressPerson.name,aCongressPerson.state,aCongressPerson.district,aCongressPerson.score])
        
        #print "%s (%s-%s) [SCORE=%s]" % (aCongressPerson.name,aCongressPerson.state,aCongressPerson.district,aCongressPerson.score)


# Sort by the score:
UncoveredList.sort(key=itemgetter(3))
UncoveredList.reverse()


Uncovered_Primary_Counter=0
# Print the uncovered list sorted by score:
for Uncovered in UncoveredList:
    Uncovered_Primary_Counter+=1
    print "%d)  %s (%s-%s) [SCORE=%s]" % (Uncovered_Primary_Counter,Uncovered[0],Uncovered[1],Uncovered[2],Uncovered[3])

    





# Added by RCG 2013:
print """
#######################################################################
SUMMARY 
#######################################################################
"""

# Sort by the number of primaries:
PrimarySummaryList.sort(key=itemgetter(1))
PrimarySummaryList.reverse()

for aTeamMember in TeamMemberList:
    #Check for match
    Check=0
    for Member in PrimarySummaryList:
        if (aTeamMember.name==Member[0]):
            Check=1
    if Check==0:
        PrimarySummaryList.append([aTeamMember.name,0])

Total_Primary_Counter=0
Tripper_Counter=0

for Member in PrimarySummaryList:
    Total_Primary_Counter+=Member[1]
    Tripper_Counter+=1
    print "%d) %s has %d Primaries<br>" %(Tripper_Counter,Member[0],Member[1])

    
print "-------------------------<br>"
print "Total: %d Primaries Covered<br>" %Total_Primary_Counter

print "There are %d Contested Primaries.<br>"  %Contested_Primary_Counter

NoConnections=Uncovered_Primary_Counter-Contested_Primary_Counter
print "There are %d Uncovered Primaries (no tripper connections).<br>"  %NoConnections



#Sum=Total_Primary_Counter+Contested_Primary_Counter+Uncovered_Primary_Counter

#print "Unitarity Check: %d +%d +%d = %d \n" %(Total_Primary_Counter,Contested_Primary_Counter,Uncovered_Primary_Counter,Sum)

#print "Total number from database:%d\n" %Congress_Person_Counter
