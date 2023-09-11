import React from "react";
const useScrollPagination = (fetchData, skipAmount, limit) => {
  const
    [data, setData] = React.useState([]),
    [skip, setSkip] = React.useState(skipAmount),
    [isLast, setIsLast] = React.useState(false),
    [isLoading, setLoading] = React.useState(true),
    [error, setError] = React.useState('')


  const handleScrollPagination = (e) => {
    const
      target = e.target,
      scrollHeight = target.documentElement.scrollHeight,
      scrollTop = target.documentElement.scrollTop,
      innerHeight = window.innerHeight

    if (scrollHeight - (scrollTop + innerHeight) < 50) {
      setLoading(true)
    }
  }

  React.useEffect(() => {
    if (isLoading) {
      fetchData()
        .then(res => res.json())
        .then(res => {
          setData([...data, ...res.images])
          setSkip(skip + limit)
          setIsLast(res.images.length < limit)
        })
        .catch(console.log)
        .finally(() => {
          setLoading(false)
        })
    }
  }, [isLoading])

  return {data, skip, isLoading, error, isLast, handleScrollPagination}
}

export default useScrollPagination