#!/usr/bin/python3
"""
Script to downloaded webpages, extract text and merge all of them
together to create one ebook.
"""

import errno
import os
import shutil
import subprocess
import sys
from newspaper import Article


# Book name
name = "Name"
# Base url, this is used as url = mainUrl + <number of chapter>
mainUrl = "http://example.com/chapter-"
# Number of all chapter
chapters = 1
# Start from 0 or 1 ?
fromZero = False


# numerical representation of start for script
start = 0 if fromZero else 1


def runInShell(command):
  """Run giver string in shell"""
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
  process.wait()
  process.communicate()


def download(mainUrl, name, number):
  """Download webpage, extract main article, save result"""
  fileName = os.path.join('chapters', '%s-%d.txt' % (name, number))
  url = "%s%d" % (mainUrl, number)

  article = Article(url)
  article.download()
  article.parse()

  # save file
  try:
    file = open(fileName, "w")
    file.write(article.text)
    file.close()
  except OSError as err:
    print("OS error: {0}".format(err))
  except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


def main():
  """Start main downloader and converter"""
  try:
    os.makedirs("chapters")
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise

  # Download all chapters one by one
  print("Downloading...")
  for i in range(start, chapters + 1, 1):
    print("Downloading: ", name, i)
    download(mainUrl, name, i)

  # merge all chapter to one file
  print("Merging...")
  command = 'cat "chapters/%s-"{%d..%d}.txt > "%s.txt"' % (name, start, chapters, name)
  runInShell(command)

  # convert to epub
  print("Converting...")
  command = 'ebook-convert "%s.txt" "%s.epub"' % (name, name)
  runInShell(command)

  # remove download directory
  print("Removing temporary data...")
  shutil.rmtree('chapters')
  os.remove("%s.txt" % (name))

  print("Done")


# if yused standalone start the script
if __name__ == '__main__':
  main()
