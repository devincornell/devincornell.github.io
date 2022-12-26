#from cpython cimport array
#import array
from libc.stdlib cimport malloc, free
from libc.stdint cimport uint64_t

#cdef array.array int_array_template = array.array('u', []) # use to create new arrays with clone
# cdef array.array newarray
# create an array with 3 elements with same type as template
#newarray = array.clone(int_array_template, 3, zero=False)

cpdef uint64_t cy_levenshtein_dist_pairwise(
        const uint64_t[:] doc_indices, # note that this has num docs + 1 entries
        const uint64_t[:] ds, 
        uint64_t[:] distances,
    ) nogil:
    '''Computes pairwise distances between all documents in the corpus.'''
    cdef uint64_t i, j, dist
    
    cdef uint64_t ct = 0
    for i in range(len(doc_indices)-1):
        for j in range(i+1, len(doc_indices)-1):
            dist = cy_levenshtein_dist_single(ds, doc_indices[i], doc_indices[i+1]-doc_indices[i], doc_indices[j], doc_indices[j+1]-doc_indices[j])
            print(f'{corpus.doc_tokens(i)} --> {corpus.doc_tokens(j)}, {dist=}')


cpdef uint64_t cy_levenshtein_dist_single(
        const uint64_t[:] ds, 
        const uint64_t start1,
        const uint64_t size1,
        const uint64_t start2,
        const uint64_t size2,
    ) nogil:
    '''For use in distance multi.'''
    
    #cdef array.array dist_array = array.clone(int_array_template, size1, zero=False)
    #cdef uint64_t[:] distances = dist_array
    cdef uint64_t *distances = <uint64_t *> malloc(size1 * sizeof(uint64_t))
    cdef uint64_t i, j
    cdef uint64_t dist, temp_dist

    try:
        distances[0] = 0

        for i in range(1, size1+1):
            distances[i] = calc_min_two(distances[i-1], i-1)

            if ds[start1+i-1] != ds[start2]:
                distances[i] += 1
        
        for j in range(1, size2):
            dist = j + 1
            for i in range(1, size1+1):
                temp_dist = calc_min_three(dist, distances[i-1], distances[i])
                if ds[start1+i-1] != ds[start2+j]:
                    temp_dist += 1
            
                distances[i-1] = dist
                dist = temp_dist
    finally:
        free(distances)

    return dist




cpdef uint64_t cy_levenshtein_dist(const uint64_t[:] d1, const uint64_t[:] d2, uint64_t[:] distances) nogil:
    
    distances[0] = 0

    cdef int i, j
    for i in range(1, len(d1)+1):
        distances[i] = calc_min_two(distances[i-1], i-1)

        if d1[i-1] != d2[0]:
            distances[i] += 1

    cdef uint64_t dist, temp_dist
    for j in range(1, len(d2)):
        dist = j + 1
        for i in range(1, len(d1)+1):
            temp_dist = calc_min_three(dist, distances[i-1], distances[i])
            if d1[i-1] != d2[j]:
                temp_dist += 1
        
            distances[i-1] = dist
            dist = temp_dist

    return dist

cpdef uint64_t calc_min_two(const uint64_t a, const uint64_t b) nogil:
    if a <= b:
        return a
    else:
        return b

cpdef uint64_t calc_min_three(const uint64_t a, const uint64_t b, const uint64_t c) nogil:
    cdef uint64_t the_min = calc_min_two(a, b)
    
    if c < the_min:
        the_min = c
    
    return the_min

