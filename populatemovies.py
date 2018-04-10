from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MovieDB, User

engine = create_engine('sqlite:///MovieCatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create user
User1 = User(name="Rudolph", email="rvd.dekock@esteq.com")
session.add(User1)
session.commit()

# Create movies data
movie1 = MovieDB(movieName="12 Strong",
               directorName="Nicolai Fuglsig",
               coverUrl="""https://pbs.twimg.com/media/DMeS0yOVoAAA0o_.jpg""",
               description="""12 Strong tells the story of the first Special Forces team
               deployed to Afghanistan after 9/11; under the leadership of a new captain,
               the team must work with an Afghan warlord to take down the Taliban.""", category="Action", user_id=1)

session.add(movie1)
session.commit()

movie2 = MovieDB(movieName="Den of Thieves",
               directorName="Christian Gudegast",
               coverUrl="""http://t0.gstatic.com/images?q=tbn:ANd9GcSGR5IIt3ZfItcMtuPcqgLhr3qe0-Zob2lYKWgrPyfHAmwOcJ1R""",
               description="""A gritty crime saga which follows the lives of an elite
               unit of the LA County Sheriff's Dept. and the state's most successful
               bank robbery crew as the outlaws plan a seemingly impossible heist on
               the Federal Reserve Bank.""", category="Crime", user_id=1)

session.add(movie2)
session.commit()

movie3 = MovieDB(movieName="Forever My Girl",
               directorName="Bethany Ashton Wolf",
               coverUrl="""http://t3.gstatic.com/images?q=tbn:ANd9GcTl05QPUJs6_lWLGbNb6WodBWGhNC7oRtgihvZGGyIzj8mjLWvH""",
               description="""After being gone for a decade a country star returns home
               to the love he left behind.""", category="Drama", user_id=1)

session.add(movie3)
session.commit()

movie4 = MovieDB(movieName="The Final Year",
               directorName="Greg Barker",
               coverUrl="""http://t3.gstatic.com/images?q=tbn:ANd9GcRhRst-X7rFNdwyCc3tMkNVlFxvGRYJ8vgVLnGMyBAcA_HIFH0j""",
               description="""THE FINAL YEAR is a unique insiders' account of President
               Barack Obama's foreign policy team during their last year in office.
               Featuring unprecedented access inside the White House and State Department,
               THE FINAL YEAR offers an uncompromising view of the inner workings of the Obama
               Administration as they prepare to leave power after eight years.""", category="Documentary", user_id=1)

session.add(movie4)
session.commit()

movie5 = MovieDB(movieName="The road",
               directorName="Dmitrii Kalashnikov",
               coverUrl="""http://t2.gstatic.com/images?q=tbn:ANd9GcTQF_ZnJKlQb2NuLWHRbuxhUOEwyZOfNLLh3bYrhJRx-bYhjsb3""",
               description="""A documentary comprised entirely of footage from dashboard
               cameras from Russian cars.""", category="Documentary", user_id=1)

session.add(movie5)
session.commit()

movie6 = MovieDB(movieName="Django",
               directorName="Etienne Comar",
               coverUrl="""http://t3.gstatic.com/images?q=tbn:ANd9GcSnm2FczCxSnt69XUZqqI5-sfy66SvjiV0du9mfUKRRCGqVAurt""",
               description="""The story of Django Reinhardt, famous guitarist and composer,
               and his flight from German-occupied Paris in 1943.""", category="Drama", user_id=1)

session.add(movie6)
session.commit()


print "Completed"
