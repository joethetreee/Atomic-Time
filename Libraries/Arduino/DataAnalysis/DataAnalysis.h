#ifndef DATAANALYSIS_H
#define DATAANALYSIS_H

/*
Data Analysis library by Duncan Robinson
Use as you like
*/

#include "Arduino.h"

// Interpolation

template <class inputType, class listType>
unsigned int GetPos(inputType input, listType* listArr, unsigned int length, unsigned int start, unsigned int finish)
// returns position of input in an array (sorted in increasing order). Index starting with 0. If between two values, the lower index is returned
{
  unsigned int index = (start+finish)/2;
  
  if (input<=listArr[index])            // if true then input value is in first half
  {
    if (index-start==0)
      return index; 
    else
      return GetPos(input, listArr, length, start, index);
  }
  else
  {
    if (finish-index<=1)
    {
      if(input<listArr[finish])
        return index;
      else
        return finish;
    }
    else
      return GetPos(input, listArr, length, index, finish);
  }
}

template <class inputType, class listType>
unsigned int GetPos(inputType input, listType* listArr, unsigned int len)
// returns position of input in an array (sorted in increasing order). Index starting with 0. If between two values, the lower index is returned
{
  unsigned int start = 0; unsigned int finish = len-1;
  return GetPos(input, listArr, len, start, finish);   
}

int ExtractValueInt(String str, char delimiter, unsigned int pos);
float ExtractValueFlt(String str, char delimiter, unsigned int pos);

int* ExtractValuesInt(String str, char delimiter, unsigned int* pos, unsigned int number);
float* ExtractValuesFlt(String str, char delimiter, unsigned int* pos, unsigned int number);

template <class inType, class outType>
float LinearInterp(inType A_0, inType A_1, outType B_0, outType B_1, float input)              // interpolates/extrapolates input from A to B
{ 
  return float( B_0+( (B_1-B_0)* (float(input-A_0)/float(A_1-A_0)) ) );
}

template <class inType, class outType>
float LinearInterpData(inType* A, outType* B, unsigned int number, float input) // interpolates/extrapolates input from data set A to B
// note: data sets must be paired i.e. A[i] maps to B[i] for all i from 0 to number-1
{
  unsigned int i = GetPos(input, A, number);                                          // returns the position of the closest value (if between, then lower)
  
  if (i>number-2)                  // if the position is at the end of the array, it will be moved back one place so that the interpolation can work with two values
    i = number-2;                  // now A[i] is the second-last element of A
  
  return LinearInterp(A[i], A[i+1], B[i], B[i+1], input);
}

// Maths

double sin_f(double x);              // period of 1.0
double cos_f(double x);              // period of 1.0
double tan_f(double x);              // period of 1.0

double asin_f(double x);             // period of 1.0
double acos_f(double x);             // period of 1.0
double atan_f(double x);             // period of 1.0

template <class inType>              // returns sign of number. 0 -> 0
signed char Sign(inType input)
{
  return (signed char)( int(input>0) - int(input<0) );
}

template <class inType, class outType>
outType iPow(inType a, unsigned int b)
/* returns a^b. b must be an unsigned integer */
{
  outType value = 1;
  for (int i = 0; i<b; i++)
  {
    value  *= a;
  }
  return value;
}

template <class inType>
inType GetModSq(unsigned int len, inType* data)
{
  return GetModSq(len, data, 0, len);
}
template <class inType>
inType GetModSq(unsigned int len, inType* data, unsigned int i1, unsigned int i2)
{
  inType tot = 0;
  for (unsigned int i=i1; i<i2; i++)
  {
    tot += data[i]*data[i];
  }
  return tot;
}

template <class inType>
double GetMod(unsigned int len, inType* data, unsigned int i1, unsigned int i2)
{
  inType modSq = GetModSq(len, data, i1, i2);
  double mod = sqrt(modSq);
  return mod;
}
template <class inType>
double GetMod(unsigned int len, inType* data)
{
  return GetMod(len, data, 0, len);
}

template <class inType>
void Normalise(unsigned int len, inType* data, unsigned int i1, unsigned int i2)
{
  double tot = GetMod(len, data, i1, i2);
  if (tot == 0)
    return;
  for (unsigned int i=i1; i<i2; i++)
  {
    data[i] /= tot;
  }
}
template <class inType>
void Normalise(unsigned int len, inType* data)
{
  Normalise(len, data, 0, len);
}


template <class dataType>
dataType Quantise(dataType input, dataType stepSize, dataType reference)
/* quantises input value using steps of size stepSize. reference is any quantised state
e.g. to quantise to nearest odd number, reference should be an odd number and step_ should be 2 */
{
  if(stepSize!=0)
  {
    int stepNumber = int( ((input - reference)/stepSize) + 0.5);        // integer number of steps from reference to quantised input value
    dataType output = reference + dataType( stepNumber*stepSize );
    return output;
  }
  else
    return input;
}

// Statistics

template <class valueType>
float Average(valueType* inputArr, unsigned int number)
{
  float output = 0;
  for (int i=0; i<number; i++)
  {
    output += inputArr[i];
  }
  output /= number;
  return output;
}

template <class valueType>
float Variance(valueType* input, unsigned int number, float avg)
{
  float sSq = 0;
  for (int i=0; i<number; i++)
  {
    sSq += iPow<float, float>(input[i], 2);  
  }
  float var = sSq / number;
  var -= iPow<float, float>(avg, 2);
    
  return var;
}
template <class valueType>
float Variance(valueType* input, unsigned int number)
{
  float avg = Average(input, number);
  return Variance(input, number, avg);  
}

template <class valType>
bool CheckRange(valType input, valType limL, valType limU, bool allowEqual=true)
// returns true if inside range
{
  if (allowEqual)
    return (input >= limL && input <= limU);
  else
    return (input > limL && input < limU);
}

template <class valType>
signed char CheckRangeDir(valType input, valType limL, valType limU, bool allowEqual=false)
// returns 0 if inside range, +1 if high and -1 if low
{
  if (allowEqual)
  {
    if (input > limU)
      return 1;
    else if (input < limL)
      return -1;
    else
      return 0;
  }
  else
  {
    if (input >= limU)
      return 1;
    else if (input <= limL)
      return -1;
    else
      return 0;
  }
}


template <class valType>
valType ScalePeriod(valType input, valType period, valType limL, valType limU)
// scales input up/down by multiples of period until it is within range. If impossible, returns input.
{
  valType output = input;

  if (input > limU)
  {
    int periodNum = (input-limU)/period;
    output -= period * periodNum;

    if (output > limU)
      output -= period;
  }

  else if (input < limL)
  {
    int periodNum = (limL-input)/period;
    output += period * periodNum;

    if (output < limL)
      output += period;
  }
  if (CheckRange(output, limL, limU))
    return output;
  else
    return input;
}

template <class valType>
valType ScalePeriod(valType input, valType period, valType limL, valType limU, bool& success)
{
  valType output = input;

  if (input > limU)
  {
    int periodNum = (input-limU)/period;
    output -= period * periodNum;

    if (output > limU)
      output -= period;
  }

  else if (input < limL)
  {
    int periodNum = (limL-input)/period;
    output += period * periodNum;

    if (output < limL)
      output += period;
  }
  if (CheckRange(output, limL, limU))
  {
    success = true;
    return output;
  }
  else
    return input;
}

// Filtering

template <class dType>
void KalFilIter(dType& xf_,dType dxp,dType xm,dType& uf_,dType dup,dType um,float A=1,float B=1,float H=1)
{
	/*
	Performs one iteration of Kalman filter
	
	~ Input variables
	returns (xf,uf)
	x,u: filter variable and its uncertainty; -f,d--p,-m: filtered, difference, measured; _: previous
	A: mixing factor for last measurement contribution; B: mixing factor for dxp; H: convert between measurement, state
	
	~ Working variables
	-t: temporary
	d-: difference
	
	~ Output variables
	dxp 
	*/
	float xft = xf_ + A*dxp; 				    // temporary new prediction of state
	float upt = A*uf_*A + dup; 			    // temporary new prediction of uncertainty
	float dx  = xm - xft; 						  // difference between measurement and temp prediction
	float umt = H*upt*H + um; 					// temporary new measurement uncertainty
	float K   = upt*H/umt; 							// Kalman gain
	xf_       = xft + K*dx;							// new filtered time
	uf_       = (1-K*H)*upt; 						// new filtered uncertainty
}
// Sorting

template <class dataType>
void Copy(dataType* dataA, dataType* dataB, unsigned int number)
{
  for (unsigned int i=0; i<number; i++)
  {
    dataB[i] = dataA[i];
  }
}


template <class dataType>
unsigned int CheckList(dataType* data, unsigned int number, unsigned int start, bool ascending)
// returns the index of first unsorted entry. Will return "number-1" if it is sorted. Starts at index start
{
  for (unsigned int i=start; i<number; i++)
  {
    if ( int(data[i] > data[i+1]) + int(!ascending) == 1 )              // will be either 0,1,2. If 1, will need to change. If 0 or 2 it is sorted
      return i;
  }
  return number-1;
}

template <class dataType>
void BubbleSort(dataType* data, unsigned int number, bool ascending)
{
  bool restart = true;
  unsigned int index = 0;
  while (index<number-1 || restart == false)  // checks whether list has been sorted
  {
    index = CheckList(data, number, index, ascending);
    if (index < number-1)                // checks if true, index and index+1 data need to be switched
    {
      dataType temp = data[index];
      data[index] = data[index+1];
      data[index+1] = temp;
      restart = false;
    }
    else if (restart == true)
    {
      break;
    }
    else
    {
      index = 0;
      restart = true;
    }
  }
}

template <class dataType>
unsigned int FindNext(dataType* data, unsigned int number, unsigned int start, dataType val)        // return position of next occurence of "val". Returns "number" if not present.
{
  for (unsigned int i=start; i<number; i++)
  {
    if (data[i] == val)
      return i;
  }
  return number;
}

template <class dataType>
void ReverseData(dataType* data, unsigned int number)
{
  dataType tempData;
  for (unsigned int i=0; i<number/2; i++)
  {
    tempData = data[i];
    data[i] = data[number-1-i];
    data[number-1-i] = tempData;
  }
}

template <class dataTypeA, class dataTypeB>
void SortGroup(dataTypeA* dataA, dataTypeB* dataB, unsigned int number, bool ascending)          // sorts low to high dataA and dataB based on dataA (low to high)
{
  dataTypeA* dataA_ = new dataTypeA [number];      // copy of original data. Needed so we know which values dataB corresponds to after dataA has been sorted.
  dataTypeB* dataB_ = new dataTypeA [number];      // copy of original data. Needed so we know original positions of each.
  bool* dataB_Used = new bool [number];            // keeps track of whether each dataB variables have been sorted (needed if there are duplicates in dataB)
  for (unsigned int i=0; i<number; i++)
  {
    dataB_Used[i] = false;
  }
    
  Copy(dataA, dataA_, number);                    // copy data from A to A_
  Copy(dataB, dataB_, number);                    // copy data from B to B_
  
  BubbleSort(dataA, number, ascending);
  
  unsigned int index = 0;
  for (unsigned int i=0; i<number; i++)
  {
    index = 0;
    bool success = false;                          // keeps track of whether a "new" occurence of dataA[i] has been found
    while (!success)
    {
      index = FindNext(dataA_, number, index, dataA[i]);
      
      if (index<number)                              // then an entry has been found
      {
        if (!dataB_Used[index])                        // then a new occurence has been found. Will update dataB.
        {
          dataB[i] = dataB_[index];
          dataB_Used[index] = true;
          success = true;
        }
      }
      else
        success = true;                          // hasn't really succeeded. There has been an error somewhere. Will cary on with algorithm to sort as best as possible
    }
  }
  
  delete [] dataA_;
  dataA_ = 0;
  delete [] dataB_;
  dataB_ = 0;
  delete [] dataB_Used;
  dataB_Used = 0;
}

#endif
