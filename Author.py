from dataclasses import dataclass

@dataclass
class Author(object):
  profile: str
  industry: str
  role: str
  firm_size: str
  deployment_architecture: str