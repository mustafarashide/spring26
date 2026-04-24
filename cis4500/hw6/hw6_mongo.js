// Question 1
var answer_1 = db.prizes.aggregate([
  {
    $match: {
      category: "physics",
      year: {
        $gte: "1960",
        $lte: "1980"
      }
    }
  },
  {
    $unwind: "$laureates"
  },
  {
    $lookup: {
      from: "laureates",
      localField: "laureates.id",
      foreignField: "id",
      as: "laureateInfo"
    }
  },
  {
    $unwind: "$laureateInfo"
  },
  {
    $match: {
      "laureateInfo.bornCountryCode": {
        $in: ["FR", "DE"]
      },
      "laureateInfo.diedCountryCode": {
        $exists: true
      },
      $expr: {
        $ne: ["$laureateInfo.bornCountryCode", "$laureateInfo.diedCountryCode"]
      }
    }
  },
  {
    $project: {
      firstname: "$laureateInfo.firstname",
      surname: "$laureateInfo.surname",
      bornCountry: "$laureateInfo.bornCountry",
      diedCountry: "$laureateInfo.diedCountry",
      _id: 0
    }
  }
])

// Question 2
var answer_2 = db.prizes.aggregate([
  {
    $unwind: "$laureates"
  },
  {
    $lookup: {
      from: "laureates",
      localField: "laureates.id",
      foreignField: "id",
      as: "laureateInfo"
    }
  },
  {
    $unwind: "$laureateInfo"
  },
  {
    $group: {
      _id: "$laureateInfo.bornCountryCode",
      laureateCount: { $sum: 1 }
    }
  },
  {
    $sort: { laureateCount: -1 }
  },
  {
    $limit: 5
  },
  {
    $project: {
      countryCode: "$_id",
      laureateCount: 1,
      _id: 0
    }
  }
])

// Question 3
var answer_3 =
  db.prizes.aggregate([
    {
      $group: {
        _id: {
          category: "$category",
          year: "$year"
        },
        numLaureates: { $sum: { $size: "$laureates" } }
      }
    },
    {
      $match: {
        numLaureates: { $gt: 1 }
      }
    },
    {
      $sort: {
        numLaureates: -1,
        "_id.year": -1,
        "_id.category": 1
      }
    },
    {
      $limit: 10
    },
    {
      $project: {
        category: "$_id.category",
        year: "$_id.year",
        numLaureates: 1,
        _id: 0
      }
    }
  ])

