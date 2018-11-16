import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import asc
from pyspark.sql.functions import expr
from pyspark.sql.functions import regexp_replace, col

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
s3_bucket = "ml-datalake-reinvent2018"
## @type: DataSource

datesource_s3_ratings = glueContext.create_dynamic_frame.from_catalog(database = "ml-data-lake", table_name = "firehose2018", transformation_ctx = "datesource_s3_ratings")
datasource_ratings = glueContext.create_dynamic_frame.from_catalog(database = "ml-data-lake", table_name = "ratings_t", transformation_ctx = "datasource_ratings")
datasource_movies = glueContext.create_dynamic_frame.from_catalog(database = "ml-data-lake", table_name = "movies_t", transformation_ctx = "datasource_movies")
datasource_links = glueContext.create_dynamic_frame.from_catalog(database = "ml-data-lake", table_name = "links_t", transformation_ctx = "datasource_links")

#s3_ratings
datasource0 = datesource_s3_ratings.toDF()
datasource0 = datasource0.withColumn("userid", expr("CAST(userid AS INTEGER)"))
datasource0 = datasource0.withColumn("movieid", expr("CAST(movieid AS INTEGER)"))
datasource0 = datasource0.select(["userid", "movieid", "ratingid", "timestamp"])
datasource0 = datasource0.filter(datasource0["userid"].isNotNull())


#ratings
datasource1 = datasource_ratings.toDF()
datasource1 = datasource1.withColumn("timestamp_c",regexp_replace("timestamp_c", "\"", ""))
datasource1 = datasource1.withColumn("userid", expr("CAST(userid AS INTEGER)"))
datasource1 = datasource1.withColumn("movieid", expr("CAST(movieid AS INTEGER)"))
datasource1 = datasource1.select(["userid", "movieid", "rating", "timestamp_c"])
datasource1 = datasource1.filter(datasource1["userid"].isNotNull())


dfUnion = datasource1.union(datasource0).sort(asc("userid"),asc("movieid"))
dfUnion.coalesce(1).write.option("header", "true").csv("s3://" + s3_bucket + "/ml/trainingdata/rating")


#movies
datasource2 = datasource_movies.toDF()
datasource2 = datasource2.withColumn("movieid", expr("CAST(movieid AS INTEGER)"))
datasource2 = datasource2.withColumn("genres",regexp_replace("genres", "\"", ""))
datasource2 = datasource2.withColumn("title",regexp_replace("title", "\"", ""))
datasource2 = datasource2.select(["movieid", "title", "genres"]).sort(asc("movieid"))
datasource2 = datasource2.filter(datasource2["movieid"].isNotNull())

datasource2.coalesce(1).write.option("header", "true").csv("s3://" + s3_bucket + "/ml/trainingdata/movies")

#links
datasource3 = datasource_links.toDF()
datasource3 = datasource3.withColumn("movieid", expr("CAST(movieid AS INTEGER)"))
datasource3 = datasource3.withColumn("tmdbid",regexp_replace("tmdbid", "\"", ""))
datasource3 = datasource3.select(["movieid", "imdbid", "tmdbid"]).sort(asc("movieid"))
datasource3 = datasource3.filter(datasource3["movieid"].isNotNull())

datasource3.coalesce(1).write.option("header", "true").csv("s3://" + s3_bucket + "/ml/trainingdata/links")


job.commit()
