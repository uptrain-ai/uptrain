from uptrain.utilities.sql_utils import execute_and_compare_sql


# Tests using spider dataset https://yale-lily.github.io/spider
if __name__ == "__main__":
    # TODO: move these to unit tests
    # Issue: Selects country as French instead of France
    predicted_sql = """
    SELECT """
    gt_query = """
    SELECT avg(age) ,  min(age) ,  max(age) FROM singer WHERE country  =  'France'
    """
    res = execute_and_compare_sql(predicted_sql, gt_query, "/Users/bhanu/src/uptrain_experiments/llm/spider/database/concert_singer/concert_singer.sqlite")
    print(res)

    # Issue: selects wrong column
    predicted_sql = """
        SELECT s.Name, s.Song_release_year
FROM singer s
WHERE s.Age = (SELECT MIN(Age) FROM singer)
LIMIT 1;"""
    gt_query = """
        SELECT song_name ,  song_release_year FROM singer ORDER BY age LIMIT 1
        """
    res = execute_and_compare_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/concert_singer/concert_singer.sqlite")
    print(res)


    # Issue: incorrect order of select columns
    predicted_sql = "SELECT City, COUNT(Employee_ID) AS num_employees FROM employee GROUP BY City;"
    gt_query = "SELECT count(*) ,  city FROM employee GROUP BY city"
    res = execute_and_compare_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/employee_hire_evaluation/employee_hire_evaluation.sqlite")
    assert res

    # Ignore column order and row order
    predicted_sql = "SELECT City, COUNT(Employee_ID) AS num_employees FROM employee GROUP BY City order by City;"
    gt_query = "SELECT city, count(*) as cnt FROM employee GROUP BY city order by cnt"
    res = execute_and_compare_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/employee_hire_evaluation/employee_hire_evaluation.sqlite")
    assert res


    # Issue: incorrect GT query
    predicted_sql = "SELECT Name FROM teacher WHERE Hometown <> 'Little Lever Urban District'"
    gt_query = "select name from teacher where hometown != \"little lever urban district\""
    res = execute_and_compare_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/course_teach/course_teach.sqlite")
    print(res)

    # Issue: incorrect order of select columns and column case
    predicted_sql = "SELECT PetType, MAX(weight) FROM Pets GROUP BY PetType;"
    gt_query = "SELECT max(weight) ,  petType FROM pets GROUP BY petType"
    res = execute_and_compare_sql(predicted_sql, gt_query,
                      "/Users/bhanu/src/uptrain_experiments/llm/spider/database/pets_1/pets_1.sqlite")
    print(res)