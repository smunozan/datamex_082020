/*USE pubs_1;*/

/*Challenge 1 - Most Profiting Authors*/
/*Step 1: Calculate the royalties of each sales for each author*/
SELECT titleauthor.title_id as "Title ID",
	   titleauthor.au_id as "Author ID",
       (titles.price * sales.qty * titles.royalty / 100 * titleauthor.royaltyper / 100) AS "SALES ROYALTY"
FROM titleauthor
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
LEFT JOIN sales ON titles.title_id = sales.title_id;

/*Step 2: Aggregate the total royalties for each title for each author*/
SELECT titleauthor.title_id as "Title ID",
	   titleauthor.au_id as "Author ID",
       sum(titles.price * sales.qty * titles.royalty / 100 * titleauthor.royaltyper / 100) AS "SALES ROYALTY"
FROM titleauthor
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
LEFT JOIN sales ON titles.title_id = sales.title_id
GROUP BY titleauthor.au_id, titleauthor.title_id;

/*Step 3: Calculate the total profits of each author*/
SELECT titleauthor.au_id as "Author ID",
       sum(titles.price * sales.qty * titles.royalty / 100 * titleauthor.royaltyper / 100) AS "PROFIT"
FROM titleauthor
LEFT JOIN titles ON titleauthor.title_id = titles.title_id
LEFT JOIN sales ON titles.title_id = sales.title_id
GROUP BY titleauthor.au_id
ORDER BY PROFIT DESC
LIMIT 3;     