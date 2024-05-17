# Route

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Name** | **string** |  | 
**StopIds** | Pointer to **[]int32** |  | [optional] [default to []]

## Methods

### NewRoute

`func NewRoute(name string, ) *Route`

NewRoute instantiates a new Route object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRouteWithDefaults

`func NewRouteWithDefaults() *Route`

NewRouteWithDefaults instantiates a new Route object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *Route) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *Route) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *Route) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *Route) HasId() bool`

HasId returns a boolean if a field has been set.

### GetName

`func (o *Route) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *Route) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *Route) SetName(v string)`

SetName sets Name field to given value.


### GetStopIds

`func (o *Route) GetStopIds() []int32`

GetStopIds returns the StopIds field if non-nil, zero value otherwise.

### GetStopIdsOk

`func (o *Route) GetStopIdsOk() (*[]int32, bool)`

GetStopIdsOk returns a tuple with the StopIds field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStopIds

`func (o *Route) SetStopIds(v []int32)`

SetStopIds sets StopIds field to given value.

### HasStopIds

`func (o *Route) HasStopIds() bool`

HasStopIds returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


