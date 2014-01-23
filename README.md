Semeval Twitter data download script
====================

For downloading tweets distributed using IDs to protect privacy.  Uses the format of the [Semeval Twitter sentiment analysis dataset](http://www.cs.york.ac.uk/semeval-2013/task2/index.php?id=data)

Prerequisites:
--------------
[sixohsix/twitter](https://github.com/sixohsix/twitter)

	easy_install twitter

Example usage:
--------------

	python download_tweets_api.py tweeti-a.dist.tsv | tee downloaded.tsv

