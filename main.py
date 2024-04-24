import random
import requests
import sqlite3
import hashlib
import getpass


class User:
  username = ""
  email = ""

  def __init__(self, username, email):
    self.username = username
    self.email = email


class Player(User):
  publicName = ""
  __points = 0
  numberOfRounds = 0

  def __init__(self, username, email, publicName):
    super().__init__(username="NA", email="NA")
    self.publicName = publicName

  def addPoint(self):
    self.__points += 1

  def getPoints(self):
    return self.__points

  def setID(self, id):
    self.userID = id

  def getRating(self):
    if self.__points == 0:
      return float(0)
    else:
      rating = round(self.__points / self.numberOfRounds, 2)
      return rating


class Admin(User):
  __password = ""

  def __init__(self, username, email, password):
    super().__init__(username="NA", email="NA")
    self.__password = password

def oneTimeUse():
  conn = sqlite3.connect("test.db")
  c = conn.cursor()
  
  # Check if admin user already exists
  c.execute("SELECT COUNT(*) FROM Users WHERE Role='admin'")
  count = c.fetchone()[0]
  
  if count == 0:
      # Admin user does not exist, so add it
      password = "admin123"
      pwdhash = hashlib.md5(password.encode()).hexdigest()
      conn.execute(
          f"INSERT INTO Users(Username,Email,Role,Password) VALUES('root','giggle@id.lv','admin','{pwdhash}');"
      )
      conn.commit()
  else:
      # Admin user already exists, update the password
      password = "admin123"
      pwdhash = hashlib.md5(password.encode()).hexdigest()
      conn.execute(
          f"UPDATE Users SET Password='{pwdhash}' WHERE Role='admin';"
      )
      conn.commit()
  
  conn.close()


class Game:
  numberOfPlayers = 0
  numberOfRounds = 0
  players = []
  url = "https://randomuser.me/api/?results=1&inc=name"

  def get_random_publicname(self):
    # Make a request to the API
    response = requests.get(self.url)

    # Check if the request was successful
    if response.status_code == 200:
      # Extract the name from the response
      data = response.json()
      results = data.get("results", [])

      # Extract the first name and last name from the result
      if results:
        username = results[0]["name"]["first"] + results[0]["name"]["last"]
        return username
      else:
        print("Error: No results found in the API response")
        return None
    else:
      # If the request was not successful, print an error message
      print("Error: Failed to retrieve data from the API")
      return None

  def __init__(self):
    self.numberOfPlayers = int(input("How many players?:"))
    
    if (self.numberOfPlayers < 0):
      username = input("Username:")
      password = getpass.getpass("Password:")
      pwdhash = hashlib.md5(password.encode()).hexdigest()
      response = self.checkForAdmin(username, pwdhash)
      
      if (response == 0):
        print("INVALID USERNAME OR PASSWORD")
        quit()  # Quits the program
      print("Options:\n1:see users\n2:clear results")
      option = int(input("Which?"))
      
      if (option == 1):
        self.__seeUsers()
      
      if (option == 2):
        self.__clearResults()
      quit()
        
    self.numberOfRounds = int(input("How many rounds:"))
    
    for i in range(self.numberOfPlayers):
      name = input(f"Player {i+1}, Enter your username:")
      email = input(f"Player {i+1}, Enter your email:")
      email = email + "@game.com"
      publicName = self.get_random_publicname()
      print(f"Player {i+1}, I will give you public name:{publicName}")
      
      if (self.checkForPlayer(name, email) == 0):
        self.insertPlayer(name, email)
      id = self.checkForPlayer(name, email)
      p = Player(name, email, publicName)
      p.setID(id)
      self.players.append(p)

      #check for payer in table
      # if not exists, Create and get ID
      # if exists, get ID
  def __clearResults(self):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    conn.execute(f"delete from results;")
    conn.commit()
    conn.close()
    print("Results cleared!")

  def __seeUsers(self):
    def queryResults():
      conn = sqlite3.connect("test.db")
      cur = conn.cursor()
      query = """
      SELECT Users.Username, Users.Email, Results.Points, Results.MaxPoints, Results.Rating
      FROM Users
      INNER JOIN Results ON Users.UserID = Results.UserID
      WHERE Results.Rating IS NOT NULL
      ORDER BY Results.Rating DESC
      """

      cur.execute(query)
      res=cur.fetchall()
      conn.close()
      return res

    result=queryResults()
    print("Users:")
    print()
    if result:  # Check if there are results
      print("Username".ljust(20), "Email".ljust(30), "Points".ljust(10), "MaxPoints".ljust(10), "Rating".ljust(10)) 
      print()
      for r in result:
          username, email, points, max_points, rating = r
          print(username.ljust(20), email.ljust(30), str(points).ljust(10), str(max_points).ljust(10), str(rating).ljust(10))
    else:
        print("No results found")

  def insertPlayer(self, username, email):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    conn.execute(
        f"insert into Users(Username,Email,Role) values('{username}','{email}','user');"
    )
    conn.commit()
    conn.close()

  def checkForPlayer(self, username, email):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    res = c.execute(
        f"SELECT UserID from Users where Username='{username}' and Email='{email}'"
    )
    result = res.fetchall()
    conn.commit()
    conn.close()
    if len(result) == 0:  #there are no such records
      return 0
    else:
      return result[0][0]

  def checkForAdmin(self, username, pwdhash):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    res = c.execute(
        f"SELECT UserID from Users where Role='admin' and Username='{username}' and Password='{pwdhash}'"
    )
    result = res.fetchall()
    conn.commit()
    conn.close()
    if len(result) == 0:  #there are no such records
      return 0
    else:
      return result[0][0]

  def startGame(self):
    maxNumber = 10
    maxPoints = self.numberOfRounds
    print(f"There are {self.numberOfPlayers} players")
    
    for iRound in range(0, self.numberOfRounds):
      theNumber = random.randint(1, maxNumber)
      print("----------------------")
      print(f"Round {iRound+1}")
      print(f"Number guessing range: 1-{maxNumber}")
      guesses = []
      
      for i in range(self.numberOfPlayers):
        guess = int(input(f"Player {i+1}, Enter your guess:"))
        guesses.append(guess)
      print(f"The correct answer was {theNumber}")
      
      for i in range(self.numberOfPlayers):
        
        if (guesses[i] == theNumber):
          print(f"{self.players[i].publicName} was right, one point")
          self.players[i].addPoint()
        
        else:
          print(f"{self.players[i].publicName} was wrong")
      print("Round ended, scores:")
      
      for player in self.players:
        print(
            f"{player.publicName}: {player.getPoints()}")
        player.numberOfRounds += 1

    for player in self.players:
      self.insertResult(player.userID, player.publicName, player.getPoints(), maxPoints, player.getRating())

    self.queryResults()
    return maxPoints

  def insertResult(self, userID, publicName, points, maxPoints, rating):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    conn.execute(
      f"INSERT INTO Results(UserID,  PublicName, Points, MaxPoints, Rating) VALUES (?, ?, ?, ?, ?)",
        (userID, publicName, points, maxPoints, rating))
    conn.commit()
    conn.close()

  def queryResults(self):
    print()
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    query = """
    SELECT PublicName, Points, MaxPoints, Rating FROM Results
    WHERE Results.Rating IS NOT NULL
    ORDER BY Results.Rating DESC
    """

    cur.execute(query)
    res = cur.fetchall()
    conn.close()

    print("Place".ljust(5), "PublicName".ljust(20), "Points".ljust(10), "MaxPoints".ljust(10), "Rating".ljust(10))
    print()
    for i, r in enumerate(res, start=1):
        publicName, points, max_points, rating = r
        print(str(f"{i}.").ljust(5), str(publicName).ljust(20), str(points).ljust(10), str(max_points).ljust(10), str(rating).ljust(10))
    

def CreateDB():
  conn = sqlite3.connect("test.db")
  c = conn.cursor()

  createSQL = '''CREATE TABLE IF NOT EXISTS Users
   (UserID integer primary key AUTOINCREMENT,
   Username varchar(255),
   Email varchar(255),
   Role varchar(255),
   Password varchar(255)
   );'''
  conn.execute(createSQL)
  createSQL = '''CREATE TABLE IF NOT EXISTS Results
   (ResultID integer primary key AUTOINCREMENT,
   UserID INT,
   PublicName varchar(255),
   Points INT,
   MaxPoints INT,
   Rating FLOAT
   );'''
  conn.execute(createSQL)

  conn.commit()
  conn.close()


###########################################################
CreateDB()
# a1=Admin("root","epasts","parole34")
# print(a1.username)
# print(a1.email)
# print(a1.askNicelyThePassword())
oneTimeUse()
g1 = Game()
g1.startGame()



