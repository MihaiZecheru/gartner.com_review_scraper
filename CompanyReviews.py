import requests, json
from Review import Review

class CompanyReviews(object):
  csv_attributes: str
  reviews: list
  company_name: str
  file_name: str
  file: any
  app: any
  remaining_progress: int

  def __init__(self, url: str, csv_attributes: list[str], app) -> None:
    """ Initialize an object of the CompanyReviews class """

    """ get review ids from html """
    self.app = app
    self.remaining_progress = 100
    raw_content = requests.get(url).text
    self.app.increment_progress_bar(15)
    self.remaining_progress -= 15


    # get index of the beginning and end of the json from the raw html
    start_of_json = raw_content.index('"userReviews":') + 14
    end_of_json = raw_content.index(',"totalCount":')

    # the array of reviews from the website
    review_ids = [review.get("reviewId") for review in json.loads(raw_content[start_of_json : end_of_json])]
    self.app.increment_progress_bar(15)
    self.remaining_progress -= 15

    product_name_short = url[url.index('/vendor/') + 8 : url.index('/product')]
    product_name_full = url[url.index('/product/') + 9 : -1]

    self.csv_attributes = csv_attributes
    self.reviews = []

    for i, review_id in enumerate(review_ids):
      self.reviews.append(Review(review_id, product_name_short, product_name_full))
      self.app.increment_progress_bar((self.remaining_progress - 5) / (len(review_ids) - i))
      self.remaining_progress -= (self.remaining_progress - 5) / (len(review_ids) - i)

    self.company_name = self.reviews[0].is_for
    self.file_name = f"{f'{self.company_name}_whole_vendor'.replace(' ', '_')}.csv"
    self.file = self.generate_csv()

    self.app.increment_progress_bar(5)

  def generate_csv(self) -> None:
    self.file = open(self.file_name, "w")

    # write the header of the csv
    header_line = "".join(f"{item}," for item in self.csv_attributes)
    self.file.write(f"{header_line[:-1]}\n")

    # create the file lines
    for review in self.reviews:
      self.file.write(
        f'"{review.is_for}","{review.author.profile}","{review.author.industry}","{review.author.role}","{review.author.firm_size}","{review.author.deployment_architecture}","{review.url}","{review.comments}","{review.like_most}","{review.dislike_most}","{review.rating}","{review.integration_and_deployment_rating}","{review.services_and_support_rating}","{review.product_capabilities_rating}"\n'
      )

    ratings_attributes = [
      "rating", "integration_and_deployment_rating",
      "services_and_support_rating", "product_capabilities_rating"
    ]

    averages = [self.average_of_attr(attr) for attr in self.csv_attributes if attr in ratings_attributes]

    averages_line = "".join(f"{ratings_attributes[i]}: {average},"
                            for i, average in enumerate(averages))
    # add "averages" line
    self.file.write(f"\n\"AVERAGES FOR: {self.company_name} -->\",{averages_line}"[:-1])

    self.file.close()
    self.file = open(self.file_name, "r")
  
  def average_of_attr(self, attr_name: str) -> float:
    sum = 0

    for review in self.reviews:
      if attr_name == "rating":
        sum += review.rating
      elif attr_name == "integration_and_deployment_rating":
        sum += review.integration_and_deployment_rating
      elif attr_name == "services_and_support_rating":
        sum += review.services_and_support_rating
      else: # attr_name is "product_capabilities_rating"
        sum += review.product_capabilities_rating

    return round(sum / len(self.reviews), 2)