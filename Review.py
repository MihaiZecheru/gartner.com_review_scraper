import requests, json
from Author import Author


def format(s: str) -> str:
  """ Replaces all instances of " with \\", and all line breaks with \\n
  to maintain the formatting of the csv file """
  
  return s.replace('"', '\\"').replace('\n', '\\n')


class Review(object):
  attributes = ["is_for", "author_profile", "author_industry", "author_role", "author_firm_size", "author_deployment_architecture", "url", "comments", "like_most", "dislike_most", "rating", "integration_and_deployment_rating", "services_and_support_rating", "product_capabilities_rating"]

  is_for: str                                      # the name of the company the review is for
  author: Author                                     # author object: { profile, industry, role, firm_size, deployment_architecture }
  url: str                                         # url of the review
  comments: str                                    # the overall review / "overall comments" field
  like_most: str                                   # the author's greatest like
  dislike_most: str                                # the author's greatest dislike
  rating: int                                      # overall rating
  integration_and_deployment_rating: int           # integration and deployment rating
  services_and_support_rating: int                 # services and support rating
  product_capabilities_rating: int                 # product capabilities rating

  def __init__(self, review_id: int, product_name_short: str, product_name_full: str) -> None:
    """ Initialize an object of the Review class """

    """ get json from html """

    url = f"https://www.gartner.com/reviews/market/security-solutions-others/vendor/{product_name_short}/product/{product_name_full}/review/view/{review_id}"
    raw_content = requests.get(url).text

    # get index of the beginning and end of the json from the raw html
    start_of_json = raw_content.index('{"props":')
    end_of_json = raw_content.index("}</script><script") + 1

    # the json object containing the review data
    data = json.loads(raw_content[start_of_json : end_of_json])
    
    """ parse review """

    # shortcuts - "constants"
    review = data.get('props').get('pageProps').get('serverSideXHRData').get('getReviewPresentation').get('review')
    user = review.get('user')
    sections = review.get('sections')
    questions = sections[0].get('questions')

    # the name of the company the review is for
    self.is_for = format(review.get('products')[0].get('name'))

    # reviewer
    self.author = Author(
      format(user.get("title")), format(user.get("industry")),
      format(user.get("role")), format(user.get("companySize")),
      format(sections[-1].get('questions')[0].get('value'))
    )

    # review
    self.url = format(url)
    self.comments = format(review.get('summary'))
    self.like_most = format(questions[0].get('value'))
    self.dislike_most = format(questions[1].get('value'))

    # review ratings    
    self.rating = int(review.get('rating'))
    self.integration_and_deployment_rating = int(sections[2].get('ratingValue'))
    self.services_and_support_rating = int(sections[3].get('ratingValue'))
    self.product_capabilities_rating = int(sections[4].get('ratingValue'))