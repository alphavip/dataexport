#ifndef _ItemInfo_H_
#define _ItemInfo_H_


#include "base/CsvParser.h"
#include "InfoMgr.h"

namespace info
{

struct ItemInfo
{
	uint32_t id;
	uint8_t type;

	int32_t Load(const base::CsvParser::Row & row);
	virtual bool Check() { return true; }
};

typedef InfoMgr<ItemInfo> ItemInfoMgr;

}


#endif // _ItemInfo_H_