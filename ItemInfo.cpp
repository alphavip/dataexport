#include "Config.h"
#include "ItemInfo.h"


namespace info
{

int32_t ItemInfo::Load(const base::CsvParser::Row& row)
{
	this->id = row.As<uint32_t>(0);
	this->type = row.As<uint8_t>(1);

	return 0;
}

}
