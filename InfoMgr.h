//
//  InfoMgr.h
//  GameSvr
//
//  Created by AlphaChen on 2016/10/24.
//
//

#ifndef _InfoMgr_H_
#define _InfoMgr_H_

#include "base/CsvParser.h"


namespace info
{
template <typename T>
class InfoMgr
{
private:
    InfoMgr(){}
    
public:
    virtual ~InfoMgr()
    {
        for(auto& t : this->m_infos)
            delete t;
    }
    
public:
    static inline InfoMgr &Get()
    {
        static InfoMgr obj;
        return obj;
    }
    static inline InfoMgr *GetPtr()
    {
        return &Get();
    }
    
public:
    int32_t Load(const base::CsvParser::Row& row)
    {
        T* t = new T();
        t->Load(row);
        this->Add(t);
        
        return 0;
    }
    const T* Get(uint32_t id)
    {
        if(id >= this->m_infos.size())
            return nullptr;
        
        return this->m_infos[id];
    }
    void Add(const T* t)
    {
        if(this->m_infos.size() <= t->id)
            this->m_infos.resize(t->id * 2);
        assert(this->m_infos[t->id] == nullptr);
        this->m_infos[t->id] = t;
    }
    
public:
    void ForEach(std::function<int32_t (const T&)> f)
    {
        for(auto& t : this->m_infos)
        {
            if(f(*t) == 1)
                break;
        }
    }
    
    const std::vector<const T*>& GetAllInfo() const { return this->m_infos; }
    
protected:
    std::vector<const T*> m_infos;
};
    
  
}


#endif // _InfoMgr_H_
