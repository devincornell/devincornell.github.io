---
title: "New repo for cleaned NSS documents"
subtitle: "I created some python code to download US National Security Strategy documents from github for your text analysis examples."
date: "Dec 3, 2019"
id: "opened_nss_docs"
---

I created a [public GitHub repo](https://github.com/devincornell/nssdocs) to share a cleaned version of the US National Security Strategy documents in plain text. It is a nice dataset to use for text analysis demos, and you can use the [`download_nss` function](https://github.com/devincornell/nssdocs/blob/master/example_download.py) to download the docs from the public repo directly in your code.

I generated these by copy/pasting the pdf text into plain text and doing some cleaning like special character conversion and some spell-checking. Paragraphs in the text are separated by two newlines, and all paragraphs appear on the same line.

The choice of NSS documents was motivated by one of my all-time favorite articles co-authored by my former advisor John Mohr, Robin Wagner-Pacifici, and Ronald Breiger. In addition to the documents analyzed in that piece, I also copy/pasted text from the Trump 2017 NSS document. Each presidential administration since 1987 is required to produce at least one document per term, so you can easily compare the documents by administration or party. 

Mohr, J. W., Wagner-Pacifici, R., and Breiger, R. L. (2015). *Toward a computational hermeneutics.* Big Data and Society, (July–December), 1–8. ([link](https://journals.sagepub.com/doi/full/10.1177/2053951715613809))


