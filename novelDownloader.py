#!/usr/bin/python3
"""
Script to downloaded webpages, extract text and merge all of them
together to create one ebook.
"""

import errno
import os
import re

from bs4 import BeautifulSoup
from ebooklib import epub
from newspaper import Article


###### Configuration #######

# Book name
name = "Chaotic sword god"
# Base url, this is used as url = mainUrl [without number of chapter]
mainUrl = "http://gravitytales.com/novel/chaotic-sword-god/csg-chapter-"

# Number of Chapter you wish to start
startInChapter = 5

# How many chapters you wish download
numberOfChapters = 7

####### End Configuration ######



re_paragraph = re.compile(r"(.+?\n\n|.+?$)", re.MULTILINE)

chapters = []


def download(number):
	"""Download webpage, extract main article, save result"""
	url = "%s%d" % (mainUrl, number)

	article = Article(url)
	article.download()
	article.parse()

	chapterText = "%s - %d" % (name, number)
	header = False

	for match in re_paragraph.finditer(article.text):
		paragraph = match.group()
		paragraph = paragraph.strip()

		if paragraph != "Previous ChapterNext Chapter":
			if not header:
				chapterText += "<h2>%s</h2>" % (paragraph)
				header = True
			else:
				chapterText += "<p>%s</p>\n" % (paragraph)

	chapterHtml = BeautifulSoup(
		"""<html>
		<head>
				<title>...</title>
				<link rel="stylesheet" type="text/css" href="style/main.css" />
		</head>
		<body></body>
		</html>""",
		'lxml'
	)
	chapterHtml.head.title.string = article.title
	chapterHtml.body.append(chapterText)

	return str(chapterText)


def packageEbook():
	ebook = epub.EpubBook()
	ebook.set_identifier("ebook-%s" % name)
	ebook.set_title(name)
	ebook.set_language('en')
	doc_style = epub.EpubItem(
		uid="doc_style",
		file_name="style/main.css",
		media_type="text/css",
		content=open("template/style.css").read()
	)
	ebook.add_item(doc_style)

	intro_ch = epub.EpubHtml(title="Introduction", file_name='intro.xhtml')
	intro_ch.add_item(doc_style)
	intro_ch.content = """
	<html>
	<head>
			<title>Introduction</title>
			<link rel="stylesheet" href="style/main.css" type="text/css" />
	</head>
	<body>
			<h1>%s</h1>
	</body>
	</html>
	""" % (name)
	ebook.add_item(intro_ch)

	ebookChapters = []

	i = startInChapter
	for chapter_data in chapters:
		chapter = epub.EpubHtml(
			title="%s - %d" % (name, i),
			file_name='%s-%d.xhtml' % (name, i)
		)
		chapter.add_item(doc_style)
		chapter.content = chapter_data
		ebook.add_item(chapter)
		ebookChapters.append(chapter)

		i += 1

	# Set the TOC
	ebook.toc = (
		epub.Link('intro.xhtml', 'Introduction', 'intro'),
		(epub.Section('Chapters'), ebookChapters)
	)
	# add navigation files
	ebook.add_item(epub.EpubNcx())
	ebook.add_item(epub.EpubNav())

	# Create spine
	nav_page = epub.EpubNav(uid='book_toc', file_name='toc.xhtml')
	nav_page.add_item(doc_style)
	ebook.add_item(nav_page)
	ebook.spine = [intro_ch, nav_page] + ebookChapters

	epubName = existFolder(name, 0)

	filename = '%s.epub' % (epubName)
	print("Saving to '%s'" % filename)
	if os.path.exists(filename):
			os.remove(filename)
	epub.write_epub(filename, ebook, {})

def existFolder (name, cont):
	if (cont == 0):
		name = name
	else:
		name = name + str(cont)

	for existentFolder in os.listdir():
		print(existentFolder)
		if (existentFolder == name+".epub"):
			name = existFolder(name, cont+1)
			break
	return name

def main():
	"""Start main downloader and converter"""

	# Download all chapters one by one
	print("Downloading...")
	for i in range(startInChapter, numberOfChapters + 1, 1):
		print("Downloading: ", name, i)
		chapters.append(download(i))

	packageEbook()

	print("Done")


# if yused standalone start the script
if __name__ == '__main__':
	main()
