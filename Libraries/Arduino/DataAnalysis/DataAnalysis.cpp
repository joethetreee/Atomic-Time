#include "DataAnalysis.h"


String DelimitString(String str, char delimiter, unsigned int pos)
{
	unsigned int pos1=0;
	for (unsigned int i=0; i<pos; i++)
	{
		pos1 = str.indexOf(delimiter, pos1)+1; 				// get position of successive occurences
		if (pos1==0)
			return String("");													// error
	}
	int pos2 = str.indexOf(delimiter, pos1);
	if (pos2==-1)
			return String("");
	String substr = str.substring(pos1,pos2);
	return substr;
}

int ExtractValueInt(String str, char delimiter, unsigned int pos)
{
	String substr = DelimitString(str, delimiter, pos);
	return substr.toInt();
}
float ExtractValueFlt(String str, char delimiter, unsigned int pos)
{
	String substr = DelimitString(str, delimiter, pos);
	return substr.toFloat();
}

int* ExtractValuesInt(String str, char delimiter, unsigned int* pos, unsigned int number)
{
	int* valArr = new int[number+1];
	int vali = 0;									// stores how many we have come across
	bool goodVals = true;					// if false will quit
	bool takenValue = false;			// whether or not a value has been extracted
	
	int pos1=0;
	int pos2=0;
	unsigned int strLen = str.length();
	for (unsigned int i=0; i<strLen && goodVals; i++)	// there aren't actually "strLen" occurences, but we will detect last occurence and break loop
	{
		for (unsigned int j=vali; j<number; j++)				// interate through the different positions we want to check
		{
			takenValue = false;
			if (i<pos[j])																// pos[j] will only increase; if i<pos[j] then we won't get any matches here
				break;
			if (i==pos[j])															// check whether the current occurence is one we are looking for
			{
				pos2 = str.indexOf(delimiter, pos1);
				if (pos2==0)
					break;
				String substr = str.substring(pos1,pos2);
				valArr[1+vali] = substr.toInt();
				
				if (valArr[1+vali] == 0)									// check whether an error has occured (conversion return 0 if the string does not begin with integer)
				{
					if (substr.charAt(0)<'0' || substr.charAt(0)>'9')	// check whether the substr begins with number (then conversion is good)
					{
						goodVals = false;
						break;
					}
				}
				
				pos1 = pos2+1;														// set pos1 to be pos2 (we have already found next delimiter) and iterate as appropriate
				vali++;
				i++;
				takenValue = true;
			}
		}
		if (takenValue)
			continue;
		pos1 = str.indexOf(delimiter, pos1)+1; 				// get position of successive occurences
		if (pos1==0)																	// error here
			break;
	}
	valArr[0]=vali;																// record the number of occurences
	return valArr;
}
float* ExtractValuesFlt(String str, char delimiter, unsigned int* pos, unsigned int number)
{
	float* valArr = new float[number+1];
	int vali = 0;									// stores how many we have come across
	bool goodVals = true;					// if false will quit
	bool takenValue = false;			// whether or not a value has been extracted
	
	int pos1=0;
	int pos2=0;
	unsigned int strLen = str.length();
	for (unsigned int i=0; i<strLen && goodVals; i++)	// there aren't actually "strLen" occurences, but we will detect last occurence and break loop
	{
		for (unsigned int j=vali; j<number; j++)				// interate through the different positions we want to check
		{
			takenValue = false;
			if (i<pos[j])																// pos[j] will only increase; if i<pos[j] then we won't get any matches here
				break;
			if (i==pos[j])															// check whether the current occurence is one we are looking for
			{
				pos2 = str.indexOf(delimiter, pos1);
				if (pos2==0)
					break;
				String substr = str.substring(pos1,pos2);
				valArr[1+vali] = substr.toInt();
				
				if (valArr[1+vali] == 0)									// check whether an error has occured (conversion return 0 if the string does not begin with integer)
				{
					if (substr.charAt(0)<'0' || substr.charAt(0)>'9')	// check whether the substr begins with number (then conversion is good)
					{
						goodVals = false;
						break;
					}
				}
				
				pos1 = pos2+1;														// set pos1 to be pos2 (we have already found next delimiter) and iterate as appropriate
				vali++;
				i++;
				takenValue = true;
			}
		}
		if (takenValue)
			continue;
		pos1 = str.indexOf(delimiter, pos1)+1; 				// get position of successive occurences
		if (pos1==0)																	// error here
			break;
	}
	valArr[0]=vali;																// record the number of occurences
	return valArr;
}

// maths


double sin_f(double x)               // period of 1.0
{
  return sin(x*2*M_PI);
}
double cos_f(double x)               // period of 1.0
{
  return cos(x*2*M_PI);
}
double tan_f(double x)               // period of 1.0
{
  return tan(x*2*M_PI);
}

double asin_f(double x)              // period of 1.0
{
  return asin(x)/(2*M_PI);
}
double acos_f(double x)              // period of 1.0
{
  return acos(x)/(2*M_PI);
}
double atan_f(double x)              // period of 1.0
{
  return atan(x)/(2*M_PI);
}