import PureCloudPlatformClientV2
import time
import requests_oauthlib

usersApi = PureCloudPlatformClientV2.apis.UsersApi()
convApi = PureCloudPlatformClientV2.apis.ConversationsApi()
teleApi = PureCloudPlatformClientV2.apis.TelephonyProvidersEdgeApi()

ROLECOMM = '61cb8bf4-9778-41bf-a925-24d5181e1921'
ROLEEMP = 'c9a0f78e-9929-44a5-a3d2-735654885b65'

CLIENTID = r'd7656b6a-e543-4f1e-bf0c-c1f9a9ea9e8d'
CLIENTSECRET = r'IxhQfCvIMcEqNuEYbyonX_TxVTqaBaPlo1cId6lgJDA'
REDIRECTURI = 'https://www.getpostman.com/oauth2/callback'
AUTHURI = 'https://login.mypurecloud.com/oauth/authorize'


def updateToken():
    newToken = input("Please enter a new OAUTH token:\n")
    try:
        setAccessToken(newToken)
        print("Authentication successful!")
    except PureCloudPlatformClientV2.rest.ApiException:
        print("Authentication failed")

def setAccessToken(newToken):
    PureCloudPlatformClientV2.configuration.access_token = newToken
    usersApi.get_users_me()

def getOauthToken():
    oauth = requests_oauthlib.OAuth2Session(CLIENTID, redirect_uri=REDIRECTURI)
    authUrl, state = oauth.authorization_url(AUTHURI)
    
def getAllUsers():
    userList = usersApi.get_users(page_size = 400)
    return userList.entities

def flattenUserPropertiesToList(user, propertyList):
    userProperties = []
    for p in propertyList:
        if p == "managerName":
            pValue = getUserManagerName(user)
        elif p == "phoneNumber":
            pValue = extractUserPrimaryPhone(user)
        elif p == "roleNames":
            pValue = ';'.join(getUserRoleNames(user))
        elif p == "queueNames":
            pValue = ';'.join(getUserQueueNames(user))
        else:
            pValue = getattr(user,p)
        userProperties.append(pValue)
    return userProperties

def getUserManagerName(user):
    try:
        managerId = user.manager.id
        managerName = getNameFromId(managerId)
    except AttributeError:
        return
    return managerName

def getUserRoleNames(user):
    time.sleep(0.4)
    roles = usersApi.get_user_roles(user.id).roles
    roleNames = [o.name for o in roles]
    return roleNames

def getUserQueueNames(user):
    time.sleep(0.4)
    queues = usersApi.get_user_queues(user.id).entities
    queueNames = [o.name for o in queues]
    return queueNames

def extractUserPrimaryPhone(user):
    contactInfo = user.primary_contact_info
    phone = None
    for c in contactInfo:
        if ((c.media_type == 'PHONE') & (c.type == 'PRIMARY')):
            phone = c.address
    return phone

def getNameFromId(lookupId):
    time.sleep(0.4)
    user = usersApi.get_user(lookupId)
    return user.name

#def addManagerName(user):
#    try:
#        managerId = user.manager.id
#        managerName = getNameFromId(managerId)
#    except AttributeError:
#        return
#    setattr(user,"managerName",managerName)

def initiateCallFromMe(phoneNumber):
    callBody = {'phoneNumber' : phoneNumber}
    response = convApi.post_conversations_calls(callBody)
    return response

def makeBasicRtcUser(name,password):
    userResponse = createUser(name,password)
    print("User created: " + userResponse.name + "/" + userResponse.id)
    rolesResponse = assignRoles(userResponse.id,[ROLEEMP,ROLECOMM])
    print("Roles assigned")
    #teleResponse = createWebRtc(userResponse.id)
    #print(teleResponse)


def createUser(name,password):
    email = name + '@ucalgary.ca'
    requestBody = { 'name' : name,
                    'email': email,
                    'password' : password
                    }
    response = usersApi.post_users(requestBody)
    return response

def assignRoles(userId,roles):
    requestBody = roles
    response = usersApi.put_user_roles(userId,requestBody)
    return response

def createWebRtc(userId):
    name = getNameFromId(userId)
    lineName = name.lower().replace(' ','') + "_webrtc"
    requestBody = {'name':name,
                   'site':{'name':'Calgary'},
                   'base':{'name':'WebRTC'},
                   'web_rtc_user':{'id':userId},
                   'lines':{'name':lineName}
                   }
    response = teleApi.post_telephony_providers_edges_phones(requestBody)
    return response
                   
                                            

#def addQueueNameList(