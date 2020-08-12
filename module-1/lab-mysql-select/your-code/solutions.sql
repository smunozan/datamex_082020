/*USE pubs_1;*/

/*Challenge 1 - Who Have Published What At Where?*/
SELECT authors.au_id as "AUTHOR ID", au_lname as "LAST NAME", au_fname as "FIRST NAME", titles.title as "TITLE", publishers.pub_name as PUBLISHER
FROM authors
LEFT JOIN titleauthor ON authors.au_id = titleauthor.au_id
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
LEFT JOIN publishers ON titles.pub_id = publishers.pub_id;

/*Challenge 2 - Who Have Published How Many At Where?*/
SELECT authors.au_id as "AUTHOR ID", au_lname as "LAST NAME", au_fname as "FIRST NAME", publishers.pub_name as PUBLISHER, count(titles.title) as "TITLE COUNT"
FROM authors
LEFT JOIN titleauthor ON authors.au_id = titleauthor.au_id
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
LEFT JOIN publishers ON titles.pub_id = publishers.pub_id
GROUP BY PUBLISHER,authors.au_id
ORDER BY  count(titles.title) DESC;

/*Challenge 3 - Best Selling Authors*/
SELECT authors.au_id as "AUTHOR ID", au_lname as "LAST NAME", au_fname as "FIRST NAME", sum(ytd_sales) as TOTAL
FROM authors
LEFT JOIN titleauthor ON authors.au_id = titleauthor.au_id
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
GROUP BY authors.au_id
ORDER BY  sum(ytd_sales) DESC
LIMIT 3;

/*Challenge 4 - Best Selling Authors Ranking*/
SELECT authors.au_id as "AUTHOR ID", au_lname as "LAST NAME", au_fname as "FIRST NAME", COALESCE(sum(ytd_sales),0) as TOTAL
FROM authors
LEFT JOIN titleauthor ON authors.au_id = titleauthor.au_id
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
GROUP BY authors.au_id
ORDER BY  sum(ytd_sales) DESC;

/*Bonus Challenge - Most Profiting Authors*/
SELECT authors.au_id as "AUTHOR ID",
	   au_lname as "LAST NAME",
	   au_fname as "FIRST NAME",
       COALESCE(((titles.advance+titles.royalty)*(titleauthor.royaltyper/100)),0) as TOTAL
FROM authors
LEFT JOIN titleauthor ON authors.au_id = titleauthor.au_id
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
GROUP BY authors.au_id
ORDER BY  TOTAL DESC;