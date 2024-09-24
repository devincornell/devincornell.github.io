---
title: "Collecting and Managing Social Media Data"
subtitle: "Some strategies and schemas for collecting, storing, and accessing data from social media platforms."
date: "August 24, 2023"
id: "dsp2_higher_order_objects"
---

As you first sit down to design schemas for collecting and anallyzing social media data, it seems simple - the APIs are straightforward and it probably wouldn't take more than a day to program the data collection interface. Far more difficult is the challenge of storing and keeping track of that data in a way that can match your analysis needs. Here I will discuss some strategies and potential database schemas that have been useful for my own research on social media.



### Analysis Limitations

Social media data often limits the researcher to a small set of questions that can be answered.

+ **Snapshot in time**: rarely can you collect a complete historical account of activities on these platforms - information about likes, favorites, bookmarks, and other interaction measures are instead taken at a particular point in time. Even with API access that allows you to collect data from the past, the interfaces almost never allow you to get information about which user favorited or liked a post at which time. 

### Typical API Interface

I have found that social media API requests typically fall into two categories: paginated and non-paginated. Non-paginated interfaces are the easiest because you will typically request and receive a fixed set of resources, whereas paginated interfaces require more effort because they require an undetermined number of requests and can be very large in number. In paginated requests, you will receive results in chunks with page ids that are returned after each subsequent request.


##### Request blocks

For the purposes of data collection, I further organize API interfaces into _request blocks_, or groups of API requests being initiated for a common purpose. I use the concept slightly differently in other jobs.

The need for the request block concept arises in non-paginated requests when you may only request a fixed and relatively small set of resources in a single request and may need to create a large number of requests to capture the full set of resources you are interested in. The need for request blocks in paginated requests arises because the response of the first request will lead you to request the next page, and so on - the requests are chunked into pages.


##### Non-paginated

Non-paginated requests are simplest because you will request and receive a fixed number of resources using the API. This is common for situations when you want to get information about a specific set of users or posts.

    > make request to server
    > receive results
    > store results in database

##### Paginated

    > make initial request
    > receive and store results
    > while there is more data to be requested (page id or last timestamp)
        > make another request
        > receive and store results


### Request Schema

+ _request block timestamp_: time of the first request made in this block
+ _pagination id_: page of request being made (0 for first request, NULL in non-paginated requests).
+ _request timestamp_: the timestamp in which the individual request was made.
+ _request endpoint_: the endpoint that the request is being sent to.
+ _target_: information about the specific resource being requested. Could be conversation id, post id, user id, or any other key information about the request
+ _number of results_: metadata about the number of results that the request returned
+ _last id_


### Snapshots in Time

The first important aspect of collecting social media data is that

