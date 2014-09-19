class Util:
  @staticmethod
  def reverse_sorted(list):
    res = sorted(list)
    res.reverse()
    return res

  @staticmethod
  def uniq_by_sorted(list):
      res = {}
      for obj in list:
          a = [c.name for c in obj]
          k = str.join("",sorted(a))
          if not res.get(k):
              res[k] = obj

      return res.values()